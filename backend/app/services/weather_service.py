import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

async def get_weather_by_coords(lat: float, lon: float) -> dict:
    """Fetch live weather data for given coordinates"""
    async with httpx.AsyncClient() as client:
        # Current weather
        weather_resp = await client.get(f"{BASE_URL}/weather", params={
            "lat": lat, "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        })
        weather = weather_resp.json()

        # If API key is invalid or not yet active, OpenWeather returns an error like {'cod': 401, 'message': '...'}
        if "main" not in weather:
            error_msg = weather.get("message", "Failed to fetch weather data. Check OpenWeather API key.")
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Weather API Error: {error_msg}")

        # 5-day forecast
        forecast_resp = await client.get(f"{BASE_URL}/forecast", params={
            "lat": lat, "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 8  # next 24 hours (3h intervals)
        })
        forecast = forecast_resp.json()

    return {
        "location": {
            "name": weather.get("name", "Unknown"),
            "country": weather.get("sys", {}).get("country", ""),
            "lat": lat,
            "lon": lon
        },
        "current": {
            "temperature": weather["main"]["temp"],
            "feels_like": weather["main"]["feels_like"],
            "humidity": weather["main"]["humidity"],
            "pressure": weather["main"]["pressure"],
            "wind_speed": weather["wind"]["speed"],
            "wind_direction": weather["wind"].get("deg", 0),
            "rainfall_1h": weather.get("rain", {}).get("1h", 0),
            "rainfall_3h": weather.get("rain", {}).get("3h", 0),
            "description": weather["weather"][0]["description"],
            "icon": weather["weather"][0]["icon"],
            "visibility": weather.get("visibility", 10000)
        },
        "forecast": [
            {
                "time": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "rainfall": item.get("rain", {}).get("3h", 0),
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            }
            for item in forecast.get("list", [])
        ]
    }

async def get_weather_by_city(city: str) -> dict:
    """Fetch weather by city name, then delegate to coords"""
    async with httpx.AsyncClient() as client:
        geo_resp = await client.get("https://api.openweathermap.org/geo/1.0/direct", params={
            "q": city, "limit": 1, "appid": OPENWEATHER_API_KEY
        })
        geo = geo_resp.json()
        if not geo:
            return {"error": f"City '{city}' not found"}
        lat, lon = geo[0]["lat"], geo[0]["lon"]

    return await get_weather_by_coords(lat, lon)
