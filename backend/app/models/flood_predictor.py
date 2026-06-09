import os
import joblib
import numpy as np

# Global cache for the ML model so we don't load it on every request
_ml_model = None

def load_model():
    global _ml_model
    if _ml_model is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'flood_rf_model.joblib')
        if os.path.exists(model_path):
            _ml_model = joblib.load(model_path)
    return _ml_model

def predict_flood_risk(
    rainfall: float,
    humidity: float,
    temperature: float,
    wind_speed: float,
    river_level: float = 0,
    lat: float = 0,
    lon: float = 0
) -> dict:
    """
    ML-based flood risk predictor using trained Random Forest model.
    Falls back to rule-based logic if model file is not found.
    """
    model = load_model()
    
    if model:
        # Use Machine Learning
        features = np.array([[rainfall, humidity, temperature, wind_speed, river_level]])
        score = model.predict(features)[0]
    else:
        # Fallback to Rule-based
        score = 0.0
        if rainfall >= 50: score += 40
        elif rainfall >= 30: score += 30
        elif rainfall >= 15: score += 20
        elif rainfall >= 5: score += 10
        elif rainfall > 0: score += 5

        if humidity >= 90: score += 25
        elif humidity >= 80: score += 18
        elif humidity >= 70: score += 10
        elif humidity >= 60: score += 5

        if wind_speed >= 20: score += 15
        elif wind_speed >= 15: score += 10
        elif wind_speed >= 10: score += 5

        if river_level >= 5: score += 20
        elif river_level >= 3: score += 12
        elif river_level >= 1: score += 6

    # Cap at 100
    risk_score = min(max(round(float(score), 1), 0), 100)

    # Risk levels
    if risk_score >= 75:
        risk_level = "CRITICAL"
        color = "#ef4444"
        advice = "Evacuate immediately. Seek higher ground. Contact emergency services."
    elif risk_score >= 55:
        risk_level = "HIGH"
        color = "#f97316"
        advice = "Prepare for flooding. Move valuables. Avoid low-lying areas."
    elif risk_score >= 35:
        risk_level = "MODERATE"
        color = "#eab308"
        advice = "Monitor weather closely. Have emergency kit ready."
    else:
        risk_level = "LOW"
        color = "#22c55e"
        advice = "Conditions normal. Stay informed."

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "color": color,
        "advice": advice,
        "inputs": {
            "rainfall": rainfall,
            "humidity": humidity,
            "temperature": temperature,
            "wind_speed": wind_speed,
            "river_level": river_level
        }
    }
