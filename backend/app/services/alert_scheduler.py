"""
Phase 5 — Alert Scheduler
Uses APScheduler to check flood risk for all subscribers every 30 minutes.
If a subscriber's location exceeds their risk threshold, send a WhatsApp alert.
"""
import asyncio
import os
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Singleton scheduler instance
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


async def _send_whatsapp_async(to_number: str, message: str) -> bool:
    """Send WhatsApp message via Twilio REST API (non-blocking)."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or "your_" in str(TWILIO_ACCOUNT_SID):
        print(f"[Scheduler] Twilio not configured — would have sent to {to_number}: {message[:60]}")
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                url,
                data={"From": TWILIO_FROM, "To": f"whatsapp:{to_number}", "Body": message},
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=10
            )
            if resp.status_code in (200, 201):
                print(f"[Scheduler] Alert sent to {to_number}")
                return True
            else:
                print(f"[Scheduler] Twilio error {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as exc:
            print(f"[Scheduler] Failed to send to {to_number}: {exc}")
            return False


async def run_alert_check():
    """
    Main scheduled job — runs every 30 minutes.
    Fetches all subscribers, checks their flood risk, sends alerts if threshold exceeded.
    """
    from app.db.database import get_pool
    from app.services.weather_service import get_weather_by_coords
    from app.models.flood_predictor import predict_flood_risk

    print("[Scheduler] Running alert check...")

    try:
        pool = await get_pool()
    except Exception as exc:
        print(f"[Scheduler] DB unavailable, skipping check: {exc}")
        return

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT phone_number, latitude, longitude, location_name, risk_threshold, last_alerted_at "
            "FROM alert_subscriptions WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        )
        # Ensure last_alerted_at column exists (add it if this is the first run after upgrade)
        try:
            await conn.execute(
                "ALTER TABLE alert_subscriptions ADD COLUMN IF NOT EXISTS last_alerted_at TIMESTAMP DEFAULT NULL"
            )
        except Exception:
            pass  # Column already exists

    if not rows:
        print("[Scheduler] No subscribers with location data. Skipping.")
        return

    print(f"[Scheduler] Checking {len(rows)} subscriber(s)...")

    for row in rows:
        phone    = row["phone_number"]
        lat      = row["latitude"]
        lon      = row["longitude"]
        loc_name = row["location_name"] or f"{lat:.2f},{lon:.2f}"
        threshold = row["risk_threshold"] or 60

        try:
            weather = await get_weather_by_coords(lat, lon)
            current = weather["current"]

            # --- Fetch real river discharge from GloFAS (Open-Meteo) ---
            from app.services.river_service import get_river_level
            river_data  = await get_river_level(lat, lon)
            river_level = river_data["river_level"]   # 0-10 normalised score

            risk = predict_flood_risk(
                rainfall=current["rainfall_3h"],   # mm/3h — correct unit for IMD thresholds
                humidity=current["humidity"],
                temperature=current["temperature"],
                wind_speed=current["wind_speed"],
                river_level=river_level,            # Real GloFAS data (not proxy)
                lat=lat,
                lon=lon,
                location_name=loc_name
            )
            score = risk["risk_score"]
            level = risk["risk_level"]

            print(f"[Scheduler] {loc_name}: {level} ({score:.0f}%) — threshold {threshold}%")

            if score >= threshold:
                # Cooldown check
                from datetime import datetime, timezone, timedelta
                last_alerted = row.get("last_alerted_at")
                now_utc = datetime.now(timezone.utc)
                cooldown_hours = 2
                if last_alerted:
                    # Ensure last_alerted is timezone-aware
                    if hasattr(last_alerted, 'tzinfo') and last_alerted.tzinfo is None:
                        last_alerted = last_alerted.replace(tzinfo=timezone.utc)
                    time_since = now_utc - last_alerted
                    if time_since < timedelta(hours=cooldown_hours):
                        print(f"[Scheduler] Skipping {loc_name} — alerted {time_since.seconds//60}min ago")
                        continue

                emoji = "🔴" if score >= 75 else "🟠"
                infra_note = f"\n⚠️ Note: {loc_name} has {risk.get('infrastructure_quality', 'average drainage')}."
                msg = (
                    f"{emoji} *FloodSenseAI ALERT*\n\n"
                    f"Flood risk at *{loc_name}* has reached "
                    f"*{level} ({score:.0f}%)*\n\n"
                    f"🌧️ Rainfall: {current['rainfall_1h']} mm/hr\n"
                    f"💧 Humidity: {current['humidity']}%\n"
                    f"🌡️ Temp: {current['temperature']}°C\n"
                    f"💨 Wind: {current['wind_speed']} m/s\n"
                    f"{infra_note}\n\n"
                    f"{'⚠️ EVACUATE or move to higher ground immediately!' if score >= 75 else '⚠️ Take precautions — monitor the situation closely.'}\n\n"
                    f"🌐 Full report: https://floodsenseai-frontend.vercel.app\n"
                    f"Reply *unsubscribe* to stop alerts."
                )
                sent = await _send_whatsapp_async(phone, msg)
                if sent:
                    async with pool.acquire() as conn2:
                        await conn2.execute(
                            "UPDATE alert_subscriptions SET last_alerted_at = $1 WHERE phone_number = $2",
                            now_utc, phone
                        )

            else:
                # --- All-clear alert: notify user when risk drops back to safe ---
                from datetime import datetime, timezone, timedelta
                last_alerted = row.get("last_alerted_at")
                if last_alerted:
                    if hasattr(last_alerted, 'tzinfo') and last_alerted.tzinfo is None:
                        last_alerted = last_alerted.replace(tzinfo=timezone.utc)
                    now_utc = datetime.now(timezone.utc)
                    # Only send all-clear if we alerted them recently (within 6h) — they're still on alert
                    if (now_utc - last_alerted) < timedelta(hours=6):
                        msg = (
                            f"✅ *FloodSenseAI: All Clear*\n\n"
                            f"Flood risk at *{loc_name}* has dropped to "
                            f"*{level} ({score:.0f}%)*\n"
                            f"Conditions are now safe at your location. 🙏\n\n"
                            f"🌐 https://floodsenseai-frontend.vercel.app"
                        )
                        sent = await _send_whatsapp_async(phone, msg)
                        if sent:
                            # Reset last_alerted_at so we don't send another all-clear immediately
                            async with pool.acquire() as conn2:
                                await conn2.execute(
                                    "UPDATE alert_subscriptions SET last_alerted_at = NULL WHERE phone_number = $1",
                                    phone
                                )
                            print(f"[Scheduler] All-clear sent to {phone} for {loc_name}")

        except Exception as exc:
            print(f"[Scheduler] Error checking {phone}: {exc}")

    print("[Scheduler] Alert check complete.")


def start_scheduler():
    """Start the APScheduler background job. Called once on app startup."""
    scheduler = get_scheduler()
    if not scheduler.running:
        # Alert check every 30 minutes
        scheduler.add_job(
            run_alert_check,
            trigger=IntervalTrigger(minutes=30),
            id="flood_alert_check",
            name="Flood Risk Alert Checker",
            replace_existing=True,
            max_instances=1,
        )

        # Keep-alive ping every 10 minutes so Render free tier never spins down.
        # Without this, Render kills the process after 15 min idle and the scheduler dies.
        async def _keep_alive():
            import httpx
            backend_url = os.getenv("RENDER_EXTERNAL_URL", "https://mark-floodsenseai.onrender.com")
            try:
                async with httpx.AsyncClient(timeout=8) as client:
                    r = await client.get(f"{backend_url}/health")
                    print(f"[KeepAlive] Pinged {backend_url}/health → {r.status_code}")
            except Exception as exc:
                print(f"[KeepAlive] Ping failed: {exc}")

        scheduler.add_job(
            _keep_alive,
            trigger=IntervalTrigger(minutes=10),
            id="keep_alive_ping",
            name="Render Keep-Alive Ping",
            replace_existing=True,
            max_instances=1,
        )

        scheduler.start()
        print("[Scheduler] Started — flood alerts every 30 min, keep-alive ping every 10 min.")


def stop_scheduler():
    """Gracefully stop the scheduler on app shutdown."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] Stopped.")
