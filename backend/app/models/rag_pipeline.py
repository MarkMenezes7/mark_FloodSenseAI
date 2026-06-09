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

    prompt = f"""You are FloodSenseAI Assistant, an expert AI system for flood risk awareness and disaster preparedness.
You help users understand flood risks, safety procedures, and emergency response.

KNOWLEDGE BASE:
{FLOOD_KNOWLEDGE}
{location_context}

USER QUESTION: {message}

Instructions:
1. If the user is asking about the flood risk or weather of a specific location (e.g., Borivali, Pune, Texas), you MUST use the `check_live_flood_risk` tool to get the real-time data before answering. Do not guess. Do not say "it's not in my knowledge base".
2. If the user's location has HIGH or CRITICAL risk, emphasize safety urgently.
3. Be concise, clear, and helpful.
4. Use emojis sparingly for readability.
5. If asked something outside flood/weather/disaster topics, gently redirect.
"""

    try:
        # We use start_chat to enable automatic tool calling
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = await chat.send_message_async(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ The AI is currently busy (Rate Limit Exceeded). Please try again in about 30 seconds."
        return f"I'm having trouble connecting to the AI right now. Please try again in a moment. For emergencies, call 112. Error: {str(e)}"
