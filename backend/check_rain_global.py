import httpx
import os
import sys
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Mix of cities worldwide - good spread across timezones and climates
cities = [
    # Southeast Asia (monsoon season!)
    "Bangkok", "Ho Chi Minh City", "Manila", "Kuala Lumpur", "Jakarta",
    "Singapore", "Colombo", "Dhaka", "Yangon",
    # Americas (daytime right now)
    "Miami", "Houston", "New Orleans", "New York", "Seattle",
    "Bogota", "Lima", "Sao Paulo", "Buenos Aires",
    # Africa
    "Lagos", "Accra", "Nairobi", "Kinshasa",
    # Europe
    "London", "Amsterdam", "Dublin", "Bergen", "Brussels",
    # Middle East / Central Asia
    "Karachi", "Islamabad",
]

print(f"{'City':<22} {'Temp':<7} {'Hum':<6} {'Rain 1h':<10} {'Weather'}")
print("-" * 72)

rainy = []
with httpx.Client(timeout=10.0) as client:
    for city in cities:
        resp = client.get("https://api.openweathermap.org/data/2.5/weather", params={
            "q": city, "appid": API_KEY, "units": "metric"
        })
        d = resp.json()
        if "main" not in d:
            continue
        temp = d["main"]["temp"]
        hum = d["main"]["humidity"]
        rain = d.get("rain", {}).get("1h", 0)
        weather = d["weather"][0]["description"]
        marker = " 🌧️ RAINING!" if rain > 0 else ""
        if rain > 0:
            rainy.append((city, rain, weather, hum, temp))
        print(f"{city:<22} {temp:<7.1f} {hum:<6} {rain:<10.2f} {weather}{marker}")

print()
print("=" * 72)
if rainy:
    print("🌧️  CITIES WITH ACTIVE RAIN RIGHT NOW:")
    for c, r, w, h, t in sorted(rainy, key=lambda x: -x[1]):
        print(f"  ✅ {c}: {r:.2f} mm/h — {w} ({h}% humidity, {t}°C)")
else:
    print("😶 No active rainfall detected in any checked city right now.")
