import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def calculate_synthetic_risk(rainfall, humidity, temp, wind, river):
    """
    Non-linear heuristic to generate realistic targets for our synthetic dataset.
    """
    score = 0.0
    
    # Rainfall is the primary driver. Non-linear scaling.
    score += (rainfall / 200.0) ** 1.5 * 50  # Up to ~50 points
    
    # River level is critical if high
    score += (river / 10.0) ** 2 * 25        # Up to 25 points
    
    # High humidity means ground is saturated or heavy rain is likely
    if humidity > 80:
        score += (humidity - 80) / 20.0 * 10 # Up to 10 points
        
    # High wind + rain = severe storm surge or cyclone
    if wind > 15:
        score += (wind / 50.0) * 15          # Up to 15 points
        
    # Temperature (minor effect, hot temps + high rain can indicate tropical storms)
    if temp > 30 and rainfall > 50:
        score += 5

    # Interaction effect: High rain + high river = catastrophic
    if rainfall > 100 and river > 6:
        score += 20
        
    # Noise to make the ML model actually learn rather than perfectly fitting a rule
    noise = np.random.normal(0, 3)
    
    return np.clip(score + noise, 0, 100)

def generate_synthetic_data(n_samples=5000):
    print(f"Generating {n_samples} synthetic weather/flood records...")
    
    # Random realistic distributions
    rainfall = np.random.exponential(scale=20, size=n_samples) # Most days little rain, some extreme
    rainfall = np.clip(rainfall, 0, 200)
    
    humidity = np.random.normal(70, 15, size=n_samples)
    humidity = np.clip(humidity, 30, 100)
    
    temperature = np.random.normal(28, 6, size=n_samples)
    temperature = np.clip(temperature, 10, 45)
    
    wind_speed = np.random.exponential(scale=5, size=n_samples)
    wind_speed = np.clip(wind_speed, 0, 50)
    
    # River level usually correlates somewhat with rainfall
    river_level = np.clip(np.random.normal(2, 1) + (rainfall / 50), 0, 10)
    
    X = np.column_stack((rainfall, humidity, temperature, wind_speed, river_level))
    
    # Generate targets
    y = np.array([
        calculate_synthetic_risk(r, h, t, w, rv)
        for r, h, t, w, rv in zip(rainfall, humidity, temperature, wind_speed, river_level)
    ])
    
    return X, y

def train_and_save_model():
    X, y = generate_synthetic_data(10000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"Model Evaluation:")
    print(f"  - Mean Absolute Error (MAE): {mae:.2f} risk points")
    print(f"  - R-squared (R2): {r2:.4f}")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save the model
    model_path = 'data/flood_rf_model.joblib'
    joblib.dump(model, model_path)
    print(f"✅ Model successfully saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
