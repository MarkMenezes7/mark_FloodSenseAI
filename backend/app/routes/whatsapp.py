import os
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.twilio_service import handle_incoming_whatsapp

router = APIRouter()

ADMIN_KEY = os.getenv("ADMIN_SECRET_KEY", "")

def _require_admin(x_admin_key: str | None):
    """Validate the admin secret key. Raises 403 if missing or wrong."""
    if not ADMIN_KEY:
        raise HTTPException(status_code=500, detail="ADMIN_SECRET_KEY not configured on server.")
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid or missing X-Admin-Key header.")


@router.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request):
    """Twilio WhatsApp webhook - handles incoming messages and location shares"""
    form_data = await request.form()
    body        = form_data.get("Body", "").strip()
    from_number = form_data.get("From", "")
    latitude    = form_data.get("Latitude")
    longitude   = form_data.get("Longitude")

    response_message = await handle_incoming_whatsapp(
        body=body,
        from_number=from_number,
        latitude=float(latitude)  if latitude  else None,
        longitude=float(longitude) if longitude else None
    )

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_message}</Message>
</Response>"""
    return PlainTextResponse(content=twiml, media_type="application/xml")


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
