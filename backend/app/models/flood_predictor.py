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
    lon: float = 0,
    location_name: str = ""
) -> dict:
    """
    Flood risk predictor with:
    - Infrastructure/drainage quality multiplier per neighborhood
    - Cumulative rainfall as river level proxy (Issue 6 fix)
    - Recalibrated scoring thresholds (Issue 5 fix)
    """
    from app.data.infrastructure_data import get_infrastructure_multiplier, get_infrastructure_description

    # -- Issue 6 Fix: Estimate river pressure from cumulative rainfall --
    # If rain_3h > 20mm, rivers start filling. We use this as a proxy
    # since we don't have a live river gauge API.
    if river_level == 0 and rainfall > 0:
        # Rainfall in last 3h is a good proxy for river pressure
        # 10mm/3h → river_level ~1, 30mm → ~3, 50mm+ → ~5
        river_level = min(rainfall / 10.0, 5.0)

    # -- Issue 5 Fix: Recalibrated rule-based scoring --
    # Thresholds based on IMD rainfall categories:
    # Light rain: <2.5mm/hr, Moderate: 2.5-7.5, Heavy: 7.5-35.5, Very heavy: 35.5-64.4, Extremely heavy: >64.4

    model = load_model()

    if model:
        features = np.array([[rainfall, humidity, temperature, wind_speed, river_level]])
        raw_score = float(model.predict(features)[0])
        # ML model may give very low scores — apply a realistic floor
        # If it's raining heavily, score should reflect that
        if rainfall >= 30 and raw_score < 30:
            raw_score = max(raw_score, 30.0)
        elif rainfall >= 15 and raw_score < 15:
            raw_score = max(raw_score, 15.0)
    else:
        # Recalibrated rule-based scoring (aligned to IMD rainfall categories)
        raw_score = 0.0

        # Rainfall (most important — 50 pts max)
        if rainfall >= 64:    raw_score += 50  # Extremely heavy rain
        elif rainfall >= 35:  raw_score += 40  # Very heavy rain
        elif rainfall >= 15:  raw_score += 28  # Heavy rain
        elif rainfall >= 7.5: raw_score += 18  # Moderate rain
        elif rainfall >= 2.5: raw_score += 10  # Light rain
        elif rainfall > 0:    raw_score += 5   # Drizzle

        # Humidity (25 pts max)
        if humidity >= 95:    raw_score += 25
        elif humidity >= 90:  raw_score += 20
        elif humidity >= 80:  raw_score += 14
        elif humidity >= 70:  raw_score += 8
        elif humidity >= 60:  raw_score += 3

        # River pressure proxy (15 pts max)
        if river_level >= 5:  raw_score += 15
        elif river_level >= 3: raw_score += 10
        elif river_level >= 1: raw_score += 5

        # Wind speed (10 pts max)
        if wind_speed >= 25:   raw_score += 10
        elif wind_speed >= 15: raw_score += 6
        elif wind_speed >= 10: raw_score += 3

    # -- Infrastructure Multiplier (Issue 5 + User Request) --
    infra_multiplier = get_infrastructure_multiplier(location_name)
    infra_description = get_infrastructure_description(infra_multiplier)

    # Apply multiplier — Virar (2.0x) floods at half the rain Borivali (1.2x) needs
    adjusted_score = raw_score * infra_multiplier

    # Cap at 100
    risk_score = min(max(round(float(adjusted_score), 1), 0), 100)

    # -- Risk levels (recalibrated) --
    if risk_score >= 70:
        risk_level = "CRITICAL"
        color = "#ef4444"
        advice = "Evacuate immediately. Seek higher ground. Contact emergency services (112)."
    elif risk_score >= 50:
        risk_level = "HIGH"
        color = "#f97316"
        advice = "Prepare for flooding. Move valuables upstairs. Avoid low-lying areas and underpasses."
    elif risk_score >= 30:
        risk_level = "MODERATE"
        color = "#eab308"
        advice = "Monitor weather closely. Have emergency kit ready. Avoid driving in waterlogged roads."
    else:
        risk_level = "LOW"
        color = "#22c55e"
        advice = "Conditions normal. Stay informed via IMD / local alerts."

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "color": color,
        "advice": advice,
        "infrastructure_multiplier": infra_multiplier,
        "infrastructure_quality": infra_description,
        "inputs": {
            "rainfall": rainfall,
            "humidity": humidity,
            "temperature": temperature,
            "wind_speed": wind_speed,
            "river_level_estimated": round(river_level, 2)
        }
    }
