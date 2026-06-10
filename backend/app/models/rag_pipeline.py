import os
import httpx
import google.generativeai as genai
from dotenv import load_dotenv
from app.models.flood_predictor import predict_flood_risk

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 1. Define the Tool for the AI
def check_live_flood_risk(location_name: str) -> dict:
    """
    Fetches real-time weather and flood risk data for ANY specific city, neighborhood, or state (e.g., Borivali, Pune, Texas).
    Always use this tool if the user asks about the weather, safety, or flood risk of a specific location.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "Weather API key not configured."}
        
    try:
        with httpx.Client(timeout=10.0) as client:
            # 1. Get coordinates
            geo_resp = client.get("https://api.openweathermap.org/geo/1.0/direct", params={
                "q": location_name, "limit": 1, "appid": OPENWEATHER_API_KEY
            })
            geo = geo_resp.json()
            if not geo:
                return {"error": f"Could not find exact location for '{location_name}'."}
            
            lat, lon = geo[0]["lat"], geo[0]["lon"]
            city_name = geo[0]["name"]
            
            # 2. Get live weather
            weather_resp = client.get("https://api.openweathermap.org/data/2.5/weather", params={
                "lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"
            })
            weather = weather_resp.json()
            
            if "main" not in weather:
                return {"error": "Failed to fetch live weather data."}

            temp = weather["main"]["temp"]
            humidity = weather["main"]["humidity"]
            wind_speed = weather["wind"]["speed"]
            
            # OpenWeather gives rain in the last 1h or 3h. Our ML model expects 3h equivalent.
            rain_1h = weather.get("rain", {}).get("1h", 0)
            rain_3h = weather.get("rain", {}).get("3h", rain_1h * 3) 

            # 3. Calculate Flood Risk using our ML Model
            risk_data = predict_flood_risk(
                rainfall=rain_3h,
                humidity=humidity,
                temperature=temp,
                wind_speed=wind_speed
            )
            
            return {
                "location_matched": city_name,
                "current_weather": weather["weather"][0]["description"],
                "temperature_celsius": temp,
                "humidity_percent": humidity,
                "rainfall_past_3h_mm": rain_3h,
                "flood_risk_score": risk_data["risk_score"],
                "flood_risk_level": risk_data["risk_level"],
                "safety_advice": risk_data["advice"]
            }
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


# 2. Configure model to use tools
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    tools=[check_live_flood_risk]
)

# Flood knowledge base - embedded directly
FLOOD_KNOWLEDGE = """
# FloodSenseAI Knowledge Base

## What is a flood?
A flood occurs when water overflows onto normally dry land. Types include:
- Flash floods: Rapid flooding from heavy rain, usually within 6 hours
- River floods: Rivers overflow their banks after prolonged rainfall
- Coastal floods: Storm surges from hurricanes/cyclones
- Urban floods: Poor drainage in cities overwhelmed by rainfall

## Flood Risk Levels
- LOW (0-34%): Normal conditions. No immediate threat.
- MODERATE (35-54%): Elevated rainfall. Monitor weather updates.
- HIGH (55-74%): Significant flood risk. Prepare emergency kit.
- CRITICAL (75-100%): Severe flood risk. Evacuate immediately.

## Before a Flood
- Know your evacuation routes
- Prepare an emergency kit: water, food, medicines, documents, torch
- Move valuables to higher floors
- Keep mobile phones charged
- Follow official weather alerts (IMD in India, NWS in USA)

## During a Flood
- Never walk or drive through floodwater (6 inches can knock you down, 12 inches can sweep a car)
- Move to higher ground immediately
- Do not touch electrical equipment if wet
- Call emergency services: India: 112, NDRF: 011-24363260

## After a Flood
- Do not return until authorities say it's safe
- Avoid floodwater — it may be contaminated
- Boil water before drinking
- Document damage for insurance claims
- Beware of structural damage to buildings

## India-Specific Flood Guidelines (NDMA)
- India receives 75% of annual rainfall in monsoon season (June-September)
- States most flood-prone: Assam, Bihar, Uttar Pradesh, Odisha, West Bengal
- NDRF (National Disaster Response Force) handles rescue operations
- IMD (India Meteorological Department) issues flood warnings
- Helpline: 1078 (NDMA), 112 (Emergency)

## Flood-Prone Cities in India
- Mumbai: Heavy rainfall + poor drainage + coastal proximity
- Chennai: Cyclone-prone, river flooding (Adyar, Cooum)
- Kolkata: Low elevation, tidal flooding
- Patna: Ganga river flooding
- Guwahati: Brahmaputra flooding

## Climate Change & Floods
- Global warming intensifies rainfall events
- Sea levels rising increases coastal flood risk
- Urban heat islands worsen flash flooding
- Deforestation reduces water absorption capacity
- SDG 13 (Climate Action) aims to reduce disaster risk

## Emergency Contacts India
- National Emergency: 112
- NDMA: 011-26701700
- Flood Control Room Delhi: 011-23379415
- Red Cross: 011-23716441
"""

async def get_rag_response(
    message: str,
    lat: float | None = None,
    lon: float | None = None,
    location_name: str | None = None,
    risk_score: float | None = None
) -> str:
    """Get a RAG-powered response from Gemini about flood-related queries"""

    # Build location context
    location_context = ""
    if location_name:
        location_context = f"\nUser's current location context: {location_name}"
    if lat and lon:
        location_context += f" (coordinates: {lat:.4f}, {lon:.4f})"
    if risk_score is not None:
        level = "CRITICAL" if risk_score >= 75 else "HIGH" if risk_score >= 55 else "MODERATE" if risk_score >= 35 else "LOW"
        location_context += f"\nCurrent flood risk at their GPS location: {level} ({risk_score:.0f}%)"

    # -- Step 1: Detect what kind of question the user is asking --
    live_data_context = ""
    msg_lower = message.lower()

    # Check A: Is the user asking a "which city is highest / most rain globally" type question?
    is_global_scan_question = any(kw in msg_lower for kw in [
        "which city", "highest flood", "highest risk", "most rain", "most rainfall",
        "where is it raining", "where is flooding", "top city", "worst city",
        "highest rainfall", "where flood", "maximum risk", "most dangerous"
    ])

    if is_global_scan_question:
        # Scan a representative set of cities with our ML model
        scan_cities = [
            "Mumbai", "Chennai", "Kolkata", "Guwahati", "Kochi",
            "Brussels", "London", "Miami", "Lagos", "Singapore",
            "Chittagong", "Dhaka", "Manila", "Jakarta", "Bangkok",
            "New Orleans", "Houston", "Ho Chi Minh City", "Colombo", "Bergen"
        ]
        city_results = []
        for city in scan_cities:
            data = check_live_flood_risk(city)
            if "error" not in data:
                city_results.append({
                    "city": data["location_matched"],
                    "score": data["flood_risk_score"],
                    "level": data["flood_risk_level"],
                    "rain": data["rainfall_past_3h_mm"],
                    "humidity": data["humidity_percent"],
                    "weather": data["current_weather"],
                })
        city_results.sort(key=lambda x: -x["score"])
        top5 = city_results[:5]
        scan_text = "\n".join([
            f"  {i+1}. {r['city']} — {r['level']} ({r['score']}%) | Rain: {r['rain']} mm/3h | Humidity: {r['humidity']}% | {r['weather']}"
            for i, r in enumerate(top5)
        ])
        live_data_context = f"""
LIVE REAL-TIME GLOBAL SCAN (20 cities checked right now using ML flood model):
Top 5 highest flood risk cities at this moment:
{scan_text}
"""

    else:
        # Check B: Is the user asking about a specific named location?
        try:
            extract_model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
            extract_response = await extract_model.generate_content_async(
                f"Extract the city/neighborhood/location name from this message (reply with ONLY the location name, or 'NONE' if no specific location is mentioned): '{message}'"
            )
            extracted_location = extract_response.text.strip().strip('"').strip("'")

            if extracted_location and extracted_location.upper() != "NONE" and len(extracted_location) < 60:
                weather_data = check_live_flood_risk(extracted_location)
                if "error" not in weather_data:
                    live_data_context = f"""
LIVE REAL-TIME WEATHER DATA (fetched right now for '{extracted_location}'):
- Location matched: {weather_data['location_matched']}
- Current weather: {weather_data['current_weather']}
- Temperature: {weather_data['temperature_celsius']}°C
- Humidity: {weather_data['humidity_percent']}%
- Rainfall (past 3h): {weather_data['rainfall_past_3h_mm']} mm
- Flood Risk Score: {weather_data['flood_risk_score']}%
- Flood Risk Level: {weather_data['flood_risk_level']}
- Safety Advice: {weather_data['safety_advice']}
"""
        except Exception:
            pass  # Fall back to knowledge base only

    prompt = f"""You are FloodSenseAI Assistant, an expert AI system for flood risk awareness and disaster preparedness.
You help users understand flood risks, safety procedures, and emergency response.

KNOWLEDGE BASE:
{FLOOD_KNOWLEDGE}
{location_context}
{live_data_context}

USER QUESTION: {message}

Instructions:
1. If LIVE REAL-TIME WEATHER DATA is provided above, use it to give a specific, accurate answer. Do NOT say you cannot provide real-time data.
2. If the live data shows LOW flood risk, tell the user the place is safe to visit from a flood perspective.
3. If the live data shows HIGH or CRITICAL risk, strongly warn the user.
4. Be concise, friendly, and helpful. Answer the user's actual question directly.
5. Use emojis sparingly for readability.
6. If asked something outside flood/weather/disaster topics, gently redirect.
"""

    try:
        simple_model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
        response = await simple_model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ The AI is currently busy. Please try again in about 30 seconds."
        return f"I'm having trouble connecting to the AI right now. Please try again in a moment. For emergencies, call 112. Error: {str(e)}"

