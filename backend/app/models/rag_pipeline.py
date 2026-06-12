import os
import httpx
import google.generativeai as genai
from dotenv import load_dotenv
from app.models.flood_predictor import predict_flood_risk

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# Read model name from env so future Google deprecations only need a Render env var update
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
genai.configure(api_key=GEMINI_API_KEY)

# ── Suburb alias map ──────────────────────────────────────────────────────────
# OWM either doesn't know these suburbs or silently matches them to wrong cities.
# Keys: lowercase suburb name → Value: (OWM-queryable city, expected country code)
# This fixes:
#   "Nalasopara" / "Nallasopara" → OWM has no entry → use Vasai-Virar
#   "Kurla"                      → OWM returns Korla, China → use Mumbai,IN
#   Other Mumbai suburbs that OWM misroutes
_SUBURB_ALIASES: dict[str, tuple[str, str]] = {
    # Mumbai Western suburbs (Vasai-Virar belt)
    "nalasopara":       ("Vasai-Virar,IN", "IN"),
    "nallasopara":      ("Vasai-Virar,IN", "IN"),
    "virar":            ("Virar,IN",       "IN"),
    "vasai":            ("Vasai,IN",       "IN"),
    "nalasopara east":  ("Vasai-Virar,IN", "IN"),
    "nalasopara west":  ("Vasai-Virar,IN", "IN"),
    # Mumbai suburbs that OWM misroutes
    "kurla":            ("Mumbai,IN",      "IN"),
    "sion":             ("Mumbai,IN",      "IN"),
    "dharavi":          ("Mumbai,IN",      "IN"),
    "bandra":           ("Mumbai,IN",      "IN"),
    "andheri":          ("Mumbai,IN",      "IN"),
    "malad":            ("Mumbai,IN",      "IN"),
    "goregaon":         ("Mumbai,IN",      "IN"),
    "kandivali":        ("Mumbai,IN",      "IN"),
    "borivali":         ("Mumbai,IN",      "IN"),
    "dahisar":          ("Mumbai,IN",      "IN"),
    "mira road":        ("Mira Bhayandar,IN", "IN"),
    "bhayander":        ("Mira Bhayandar,IN", "IN"),
    "thane":            ("Thane,IN",       "IN"),
    "kalyan":           ("Kalyan,IN",      "IN"),
    "dombivli":         ("Dombivli,IN",    "IN"),
    "badlapur":         ("Badlapur,IN",    "IN"),
    "ambernath":        ("Ambernath,IN",   "IN"),
    "panvel":           ("Panvel,IN",      "IN"),
    "kharghar":         ("Navi Mumbai,IN", "IN"),
    "vashi":            ("Navi Mumbai,IN", "IN"),
    "belapur":          ("Navi Mumbai,IN", "IN"),
    "chembur":          ("Mumbai,IN",      "IN"),
    "ghatkopar":        ("Mumbai,IN",      "IN"),
    "vikhroli":         ("Mumbai,IN",      "IN"),
    "mulund":           ("Mumbai,IN",      "IN"),
    "powai":            ("Mumbai,IN",      "IN"),
    "wadala":           ("Mumbai,IN",      "IN"),
    "parel":            ("Mumbai,IN",      "IN"),
    "worli":            ("Mumbai,IN",      "IN"),
    "lower parel":      ("Mumbai,IN",      "IN"),
    "dadar":            ("Mumbai,IN",      "IN"),
    "matunga":          ("Mumbai,IN",      "IN"),
    # Delhi NCR suburbs
    "noida":            ("Noida,IN",       "IN"),
    "gurgaon":          ("Gurugram,IN",    "IN"),
    "gurugram":         ("Gurugram,IN",    "IN"),
    "faridabad":        ("Faridabad,IN",   "IN"),
    "ghaziabad":        ("Ghaziabad,IN",   "IN"),
}

# ── Country validation ────────────────────────────────────────────────────────
# If a city is expected to be in India but OWM returns a different country,
# reject the result rather than silently serving wrong-country weather.
_INDIA_KEYWORDS = {
    "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "surat", "jaipur", "lucknow", "kanpur",
    "nagpur", "indore", "bhopal", "patna", "guwahati", "kochi", "vizag",
    "visakhapatnam", "vadodara", "rajkot", "nashik", "faridabad", "meerut",
    "assam", "bihar", "odisha", "kerala", "maharashtra", "gujarat",
}

def _resolve_location(location_name: str) -> str:
    """Apply alias map → return OWM-queryable location string."""
    return _SUBURB_ALIASES.get(location_name.lower(), (location_name, None))[0]

def _expected_country(location_name: str) -> str | None:
    """Return expected ISO country code if we know it, else None."""
    alias = _SUBURB_ALIASES.get(location_name.lower())
    if alias:
        return alias[1]
    if any(kw in location_name.lower() for kw in _INDIA_KEYWORDS):
        return "IN"
    return None


# 1. Define the Tool for the AI
def check_live_flood_risk(location_name: str) -> dict:
    """
    Fetches real-time weather and flood risk data for ANY specific city, neighborhood,
    or state (e.g., Nalasopara, Virar, Borivali, Pune, Texas).
    Always use this tool if the user asks about the weather, safety, or flood risk
    of a specific location.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "Weather API key not configured."}

    # Apply suburb alias before hitting OWM
    owm_query    = _resolve_location(location_name)
    expected_cc  = _expected_country(location_name)

    try:
        with httpx.Client(timeout=10.0) as client:
            # 1. Get coordinates
            geo_resp = client.get("https://api.openweathermap.org/geo/1.0/direct", params={
                "q": owm_query, "limit": 3, "appid": OPENWEATHER_API_KEY
            })
            geo_results = geo_resp.json()
            if not geo_results:
                return {"error": f"Could not find location '{location_name}'."}

            # Pick the first result that matches expected country (if we know it)
            geo = None
            if expected_cc:
                for result in geo_results:
                    if result.get("country", "").upper() == expected_cc.upper():
                        geo = result
                        break
            if geo is None:
                geo = geo_results[0]   # fallback to first result

            lat, lon   = geo["lat"], geo["lon"]
            city_name  = geo.get("name", owm_query)
            got_cc     = geo.get("country", "")

            # Country sanity check — reject silently wrong results
            if expected_cc and got_cc.upper() != expected_cc.upper():
                return {"error": f"Location mismatch: OWM returned '{city_name}, {got_cc}' for '{location_name}'. Try a nearby larger city."}
            
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


# 2. Configure model to use tools (model name from env — no hardcoding)
model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
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

    # -- Check 0: Hypothetical rainfall question? Answer with ML directly (0 Gemini calls) --
    # Pattern: "if it rains X mm in [city]" / "what if 70mm falls in Virar" etc.
    import re as _re
    _hypo_match = _re.search(
        r'(?:if(?:\s+it)?\s+rains?|what\s+if|assume|suppose|scenario|in\s+case)'
        r'[^\d]*([\d.]+)\s*(?:mm|millimeter)',
        msg_lower
    )
    if _hypo_match:
        hypo_rain = float(_hypo_match.group(1))
        # Try to extract city name cheaply from alias map first
        hypo_city = None
        for alias_key in _SUBURB_ALIASES:
            if alias_key in msg_lower:
                hypo_city = alias_key.title()
                break
        if not hypo_city:
            # Quick scan for common city names
            _known_cities = [
                "mumbai", "delhi", "chennai", "kolkata", "pune", "hyderabad",
                "bangalore", "bengaluru", "thane", "virar", "nalasopara",
                "navi mumbai", "guwahati", "kochi", "surat", "ahmedabad",
            ]
            for c in _known_cities:
                if c in msg_lower:
                    hypo_city = c.title()
                    break
        from app.models.flood_predictor import predict_flood_risk as _prf
        _hr = _prf(
            rainfall=hypo_rain,
            humidity=85,          # assume heavy-rain humidity
            temperature=28,
            wind_speed=8,
            river_level=min(hypo_rain / 10.0, 5.0),
            location_name=hypo_city or ""
        )
        _city_str = f" in {hypo_city}" if hypo_city else ""
        _infra = f" (infrastructure multiplier: {_hr['infrastructure_multiplier']}x — {_hr['infrastructure_quality']})" if hypo_city else ""
        return (
            f"If it rains **{hypo_rain:.0f} mm in 3 hours{_city_str}**, the estimated flood risk would be:\n\n"
            f"**{_hr['risk_score']:.0f}% — {_hr['risk_level']} RISK**{_infra}\n\n"
            f"{_hr['advice']}\n\n"
            f"_Note: This is a hypothetical estimate based on rainfall alone. "
            f"Actual risk depends on real-time river levels, soil saturation, and local drainage._"
        )


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
            extract_model = genai.GenerativeModel(model_name=GEMINI_MODEL)
            extract_response = await extract_model.generate_content_async(
                f"Extract the city, suburb, neighborhood, or location name from this message. "
                f"Indian suburb names like 'Nalasopara', 'Virar', 'Kurla', 'Thane', 'Badlapur', "
                f"'Borivali', 'Andheri', 'Noida', 'Gurugram' are valid locations — always extract them. "
                f"Reply with ONLY the location name, or 'NONE' if no specific location is mentioned.\n"
                f"Message: '{message}'"
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
        except Exception as e429:
            if "429" in str(e429):
                # Extractor hit rate limit — skip live data, answer from knowledge base only
                # This saves the second (main) Gemini call from also hitting 429
                pass
            # Fall back to knowledge base only

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
        simple_model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = await simple_model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            # Rate limited — answer from knowledge base without Gemini
            # Build a minimal but useful response from the knowledge base context
            kb_note = (
                "_[AI assistant is temporarily rate-limited. Answering from knowledge base.]_\n\n"
            )
            if live_data_context:
                # We have live data — extract key facts and answer directly
                return (
                    kb_note +
                    "Here is the live data I fetched for your location:\n" +
                    live_data_context.strip() +
                    "\n\nFor emergencies call **112** (India) or your local emergency number."
                )
            return (
                kb_note +
                "Mumbai and surrounding areas flood during heavy monsoon rainfall due to:\n"
                "- Poor stormwater drainage capacity (only handles ~25mm/hr)\n"
                "- Low-lying coastal geography\n"
                "- Encroachment on natural water bodies and mangroves\n"
                "- Simultaneous high tides blocking drainage outflows\n\n"
                "For emergencies: **112** | NDMA: **1078** | IMD alerts: imd.gov.in"
            )
        return f"I'm having trouble connecting right now. For emergencies, call 112. ({str(e)[:80]})"
