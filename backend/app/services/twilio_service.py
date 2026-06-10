import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

async def handle_incoming_whatsapp(
    body: str,
    from_number: str,
    latitude: float | None = None,
    longitude: float | None = None
) -> str:
    """Handle incoming WhatsApp message from user"""
    from app.services.weather_service import get_weather_by_coords
    from app.models.flood_predictor import predict_flood_risk

    # User shared their live location
    if latitude and longitude:
        try:
            weather = await get_weather_by_coords(latitude, longitude)
            current = weather["current"]
            location = weather["location"]
            risk = predict_flood_risk(
                rainfall=current["rainfall_1h"],
                humidity=current["humidity"],
                temperature=current["temperature"],
                wind_speed=current["wind_speed"],
                river_level=0,
                lat=latitude,
                lon=longitude
            )
            level = risk["risk_level"]
            score = risk["risk_score"]
            emoji = "🔴" if score > 70 else "🟡" if score > 40 else "🟢"

            return (
                f"📍 *FloodSenseAI Report*\n"
                f"Location: {location['name']}, {location['country']}\n\n"
                f"{emoji} *Flood Risk: {level} ({score:.0f}%)*\n\n"
                f"🌧️ Rainfall: {current['rainfall_1h']} mm/hr\n"
                f"💧 Humidity: {current['humidity']}%\n"
                f"🌡️ Temp: {current['temperature']}°C\n"
                f"💨 Wind: {current['wind_speed']} m/s\n\n"
                f"{'⚠️ ALERT: Take precautions immediately!' if score > 70 else '✅ Conditions are currently manageable.'}\n\n"
                f"🌐 Full report: https://floodsenseai-frontend.vercel.app"
            )
        except Exception as e:
            return f"❌ Could not fetch flood data for your location. Please try again. Error: {str(e)}"

    # Text message handling
    body_lower = body.lower()
    if any(w in body_lower for w in ["hi", "hello", "hey", "start"]):
        return (
            "👋 Welcome to *FloodSenseAI* 🌊\n\n"
            "I can help you with real-time flood risk information!\n\n"
            "📍 *Share your location* (Tap the 📎 or ➕ icon > Location)\n"
            "🌆 Or just type any city name below\n"
            "ℹ️ Type *!help* for all commands\n\n"
            "Stay safe! 🙏"
        )
    elif "!help" in body_lower:
        return (
            "📋 *FloodSenseAI Commands*\n\n"
            "📍 Share Location → Flood risk for your exact location\n"
            "🌆 City name → e.g. type 'Mumbai'\n"
            "📊 'risk' → Current risk summary\n"
            "🔔 'subscribe' → Get automatic alerts\n"
            "❌ 'unsubscribe' → Stop alerts\n\n"
            "🌐 Full dashboard: https://floodsenseai-frontend.vercel.app"
        )
    elif "subscribe" in body_lower:
        return (
            "🔔 *Alert Subscription*\n\n"
            "To subscribe for automatic flood alerts:\n"
            "1. Share your location with me\n"
            "2. I'll alert you when risk exceeds 60%\n\n"
            "📍 Please share your location now!"
        )
    elif "unsubscribe" in body_lower:
        return "✅ You have been unsubscribed from FloodSenseAI alerts. Stay safe! 🙏"
    else:
        # Try treating it as a city name
        try:
            from app.services.weather_service import get_weather_by_city
            weather = await get_weather_by_city(body)
            if "error" not in weather:
                current = weather["current"]
                location = weather["location"]
                risk = predict_flood_risk(
                    rainfall=current["rainfall_1h"],
                    humidity=current["humidity"],
                    temperature=current["temperature"],
                    wind_speed=current["wind_speed"],
                    river_level=0,
                    lat=location["lat"],
                    lon=location["lon"]
                )
                score = risk["risk_score"]
                emoji = "🔴" if score > 70 else "🟡" if score > 40 else "🟢"
                return (
                    f"📍 *{location['name']}, {location['country']}*\n"
                    f"{emoji} Flood Risk: {risk['risk_level']} ({score:.0f}%)\n"
                    f"🌧️ Rainfall: {current['rainfall_1h']} mm/hr\n"
                    f"💧 Humidity: {current['humidity']}%\n"
                    f"🌡️ Temp: {current['temperature']}°C\n\n"
                    f"🌐 https://floodsenseai-frontend.vercel.app"
                )
        except:
            pass
        return (
            "❓ I didn't understand that.\n\n"
            "Try:\n"
            "📍 Share your location (Tap 📎 > Location)\n"
            "🌆 Type a city name (e.g. Mumbai)\n"
            "ℹ️ Type *!help* for all commands"
        )

def send_whatsapp_alert(to_number: str, message: str):
    """Send a proactive WhatsApp alert to a subscriber"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=TWILIO_FROM,
            to=f"whatsapp:{to_number}",
            body=message
        )
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp to {to_number}: {e}")
        return False
