import os
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.twilio_service import handle_incoming_whatsapp

router = APIRouter()

ADMIN_KEY = os.getenv("ADMIN_SECRET_KEY", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

def _require_admin(x_admin_key: str | None):
    """Validate the admin secret key. Raises 403 if missing or wrong."""
    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="ADMIN_SECRET_KEY not configured on server.")
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid or missing X-Admin-Key header.")


def _validate_twilio_signature(request: Request, form_data: dict) -> bool:
    """Validate the X-Twilio-Signature header to prevent spoofed webhooks."""
    if not TWILIO_AUTH_TOKEN:
        return True  # Can't validate without token — skip in dev/test
    try:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        signature = request.headers.get("X-Twilio-Signature", "")
        # Use the full URL as seen by Twilio (https)
        url = str(request.url).replace("http://", "https://")
        return validator.validate(url, form_data, signature)
    except Exception:
        return True  # If twilio lib unavailable, skip validation rather than block


@router.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request):
    """Twilio WhatsApp webhook — responds instantly (avoids 5s Twilio timeout),
    then sends the actual reply as an outbound message via background task."""
    import asyncio
    form_data   = await request.form()
    form_dict   = dict(form_data)
    body        = form_dict.get("Body", "").strip()
    from_number = form_dict.get("From", "")
    latitude    = form_dict.get("Latitude")
    longitude   = form_dict.get("Longitude")

    # Validate Twilio signature — reject spoofed requests
    if not _validate_twilio_signature(request, form_dict):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Fire reply in the background — do NOT await here, so we return instantly
    asyncio.create_task(_reply_async(
        body=body,
        from_number=from_number,
        latitude=float(latitude)  if latitude  else None,
        longitude=float(longitude) if longitude else None,
    ))

    # Return an empty TwiML response immediately so Twilio doesn't time out
    return PlainTextResponse(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


async def _reply_async(body: str, from_number: str, latitude, longitude):
    """Actually process the message and send a reply via Twilio REST API (not TwiML)."""
    import httpx, os
    from app.services.twilio_service import handle_incoming_whatsapp

    reply = await handle_incoming_whatsapp(
        body=body,
        from_number=from_number,
        latitude=latitude,
        longitude=longitude,
    )

    # Send outbound message via Twilio REST API
    sid   = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    frm   = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    url   = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url,
                data={"From": frm, "To": from_number, "Body": reply},
                auth=(sid, token)
            )
            print(f"[Webhook] Sent reply to {from_number}: HTTP {r.status_code}")
    except Exception as exc:
        print(f"[Webhook] Failed to send reply: {exc}")


@router.post("/trigger-alerts")
async def trigger_alerts_now(x_admin_key: str | None = Header(default=None)):
    """Manually trigger the alert scheduler — requires X-Admin-Key header."""
    _require_admin(x_admin_key)
    from app.services.alert_scheduler import run_alert_check
    await run_alert_check()
    return {"message": "Alert check triggered successfully", "success": True}


@router.post("/test-send")
async def test_send_whatsapp(
    phone: str,
    message: str = "Test alert from FloodSenseAI!",
    x_admin_key: str | None = Header(default=None)
):
    """Send a test WhatsApp message — requires X-Admin-Key header."""
    _require_admin(x_admin_key)
    from app.services.alert_scheduler import _send_whatsapp_async
    success = await _send_whatsapp_async(phone, message)
    return {"success": success, "to": phone}
