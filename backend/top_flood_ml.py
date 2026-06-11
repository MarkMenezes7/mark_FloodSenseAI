import sys
sys.stdout.reconfigure(encoding='utf-8')

import httpx
import os
from dotenv import load_dotenv
from app.models.flood_predictor import predict_flood_risk  # use actual ML model

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

cities = [
    "Brussels", "London", "Miami", "Lagos", "Bergen",
    "Amsterdam", "Mumbai", "Chennai", "Kolkata", "Guwahati",
    "Dhaka", "Manila", "Jakarta", "Bangkok", "Ho Chi Minh City",
    "Singapore", "Kuala Lumpur", "Colombo", "Yangon", "Kochi",
    "New Orleans", "Houston", "Seattle", "Sao Paulo", "Bogota",
    "Nairobi", "Kinshasa", "Accra", "Dublin", "Porto",
    "Tokyo", "Hong Kong", "Taipei", "Hanoi", "Chittagong",
    "Karachi", "Kathmandu", "Rangoon", "New York", "Vancouver",
]

results = []
with httpx.Client(timeout=10.0) as client:
    for city in cities:
        resp = client.get("https://api.openweathermap.org/data/2.5/weather", params={
            "q": city, "appid": API_KEY, "units": "metric"
        })
        d = resp.json()
        if "main" not in d:
            continue
        temp     = d["main"]["temp"]
        humidity = d["main"]["humidity"]
        wind     = d["wind"]["speed"]
        rain_1h  = d.get("rain", {}).get("1h", 0)
        rain_3h  = d.get("rain", {}).get("3h", rain_1h * 3)
        country  = d["sys"]["country"]
        weather_desc = d["weather"][0]["description"]

        # Use the ACTUAL ML model (same as bot uses)
        risk = predict_flood_risk(
            rainfall=rain_3h,
            humidity=humidity,
            temperature=temp,
            wind_speed=wind
        )
        score = risk["risk_score"]
        level = risk["risk_level"]
        results.append((city, country, score, level, rain_1h, humidity, wind, weather_desc))

results.sort(key=lambda x: -x[2])

print(f"\n{'Rank':<5} {'City':<24} {'Score':<8} {'Level':<10} {'Rain/hr':<10} {'Hum':<6} {'Weather'}")
print("-" * 82)
for i, (city, country, score, level, rain, hum, wind, desc) in enumerate(results[:15], 1):
    flag = "RED" if level == "CRITICAL" else "ORANGE" if level == "HIGH" else "YELLOW" if level == "MODERATE" else "GREEN"
    print(f"{i:<5} {city+', '+country:<24} {score:<8} {flag+' '+level:<16} {rain:<10.2f} {hum:<6} {desc}")

print()
print("=" * 82)
print("TOP 5 HIGHEST FLOOD RISK (using your actual ML model):")
for i, (city, country, score, level, rain, hum, wind, desc) in enumerate(results[:5], 1):
    print(f"  {i}. {city}, {country} => {level} ({score}%) | Rain: {rain:.2f} mm/hr | Humidity: {hum}%")
