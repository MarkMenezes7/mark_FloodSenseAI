import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

cities = [
    "Mumbai", "Chennai", "Kolkata", "Pune", "Goa", "Mangalore",
    "Kochi", "Hyderabad", "Bhopal", "Patna", "Guwahati", "Bhubaneswar",
    "Thiruvananthapuram", "Nagpur", "Surat", "Ahmedabad"
]

print(f"{'City':<20} {'Temp':<8} {'Humidity':<10} {'Rain(1h mm)':<14} {'Weather'}")
print("-" * 70)

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
        rain = d.get("rain", {}).get("1h", 0)
        weather = d["weather"][0]["description"]
        marker = " 🌧️ RAIN!" if rain > 0 else ""
        print(f"{city:<20} {temp:<8.1f} {humidity:<10} {rain:<14.2f} {weather}{marker}")
