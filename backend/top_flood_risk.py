import sys
sys.stdout.reconfigure(encoding='utf-8')

import httpx
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Wide mix of cities globally
cities = [
    "Brussels", "London", "Miami", "Lagos", "Bergen",
    "Amsterdam", "Mumbai", "Chennai", "Kolkata", "Guwahati",
    "Dhaka", "Manila", "Jakarta", "Bangkok", "Ho Chi Minh City",
    "Singapore", "Kuala Lumpur", "Colombo", "Yangon", "Kochi",
    "New Orleans", "Houston", "Seattle", "Sao Paulo", "Bogota",
    "Nairobi", "Kinshasa", "Accra", "Dublin", "Porto",
    "Tokyo", "Osaka", "Hong Kong", "Taipei", "Hanoi",
    "Karachi", "Islamabad", "Kathmandu", "Chittagong", "Rangoon",
]

def calc_risk(rainfall, humidity, wind_speed):
    """Rule-based flood risk calculation (same as our ML fallback)"""
    score = 0.0

    # Rainfall contribution (most important)
    if rainfall >= 50: score += 40
    elif rainfall >= 30: score += 30
    elif rainfall >= 15: score += 20
    elif rainfall >= 5:  score += 10
    elif rainfall > 0:   score += 5

    # Humidity contribution
    if humidity >= 90:   score += 25
    elif humidity >= 80: score += 18
    elif humidity >= 70: score += 10
    elif humidity >= 60: score += 5

    # Wind contribution
    if wind_speed >= 20:   score += 15
    elif wind_speed >= 15: score += 10
    elif wind_speed >= 10: score += 5

    return min(round(score, 1), 100)

results = []
with httpx.Client(timeout=10.0) as client:
    for city in cities:
        resp = client.get("https://api.openweathermap.org/data/2.5/weather", params={
            "q": city, "appid": API_KEY, "units": "metric"
        })
        d = resp.json()
        if "main" not in d:
            continue
        temp = d["main"]["temp"]
        humidity = d["main"]["humidity"]
        wind = d["wind"]["speed"]
        rain_1h = d.get("rain", {}).get("1h", 0)
        rain_3h = d.get("rain", {}).get("3h", rain_1h * 3)
        weather_desc = d["weather"][0]["description"]
        country = d["sys"]["country"]

        score = calc_risk(rain_3h, humidity, wind)
        level = "CRITICAL" if score >= 75 else "HIGH" if score >= 55 else "MODERATE" if score >= 35 else "LOW"
        results.append((city, country, score, level, rain_1h, humidity, wind, weather_desc))

# Sort by score descending
results.sort(key=lambda x: -x[2])

print(f"\n{'Rank':<5} {'City':<22} {'Score':<8} {'Level':<10} {'Rain/hr':<10} {'Hum':<6} {'Weather'}")
print("-" * 80)
for i, (city, country, score, level, rain, hum, wind, desc) in enumerate(results[:15], 1):
    flag = "🔴" if level == "CRITICAL" else "🟠" if level == "HIGH" else "🟡" if level == "MODERATE" else "🟢"
    print(f"{i:<5} {city+', '+country:<22} {score:<8} {flag+level:<12} {rain:<10.2f} {hum:<6} {desc}")

print()
print("=" * 80)
print("TOP 5 HIGHEST FLOOD RISK RIGHT NOW:")
for i, (city, country, score, level, rain, hum, wind, desc) in enumerate(results[:5], 1):
    print(f"  {i}. {city}, {country} — {level} ({score}%) | Rain: {rain:.2f} mm/hr | Hum: {hum}%")
