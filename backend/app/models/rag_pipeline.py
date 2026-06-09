import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Flood knowledge base - embedded directly (Phase 4 will add full RAG with vector store)
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
        location_context = f"\nUser's current location: {location_name}"
    if lat and lon:
        location_context += f" (coordinates: {lat:.4f}, {lon:.4f})"
    if risk_score is not None:
        level = "CRITICAL" if risk_score >= 75 else "HIGH" if risk_score >= 55 else "MODERATE" if risk_score >= 35 else "LOW"
        location_context += f"\nCurrent flood risk at their location: {level} ({risk_score:.0f}%)"

    prompt = f"""You are FloodSenseAI Assistant, an expert AI system for flood risk awareness and disaster preparedness.
You help users understand flood risks, safety procedures, and emergency response.

KNOWLEDGE BASE:
{FLOOD_KNOWLEDGE}
{location_context}

USER QUESTION: {message}

Instructions:
- Answer based on the knowledge base above
- Be concise, clear, and helpful
- If the user's location has HIGH or CRITICAL risk, emphasize safety urgently
- Use emojis sparingly for readability
- If asked something outside flood/weather/disaster topics, gently redirect
- Always end with a safety tip if risk is high
"""

    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ The AI is currently busy (Rate Limit Exceeded). Please try again in about 30 seconds."
        return f"I'm having trouble connecting to the AI right now. Please try again in a moment. For emergencies, call 112. Error: {str(e)}"
