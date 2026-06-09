from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.database import get_pool

router = APIRouter()

class AlertSubscription(BaseModel):
    phone_number: str
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    risk_threshold: int = 60

@router.post("/subscribe")
async def subscribe_alert(sub: AlertSubscription):
    """Subscribe a phone number for WhatsApp flood alerts"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO alert_subscriptions (phone_number, latitude, longitude, location_name, risk_threshold)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (phone_number) DO UPDATE
                SET latitude=$2, longitude=$3, location_name=$4, risk_threshold=$5
            """, sub.phone_number, sub.latitude, sub.longitude, sub.location_name, sub.risk_threshold)
            return {"message": f"✅ Subscribed {sub.phone_number} for flood alerts!", "success": True}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.delete("/unsubscribe/{phone_number}")
async def unsubscribe_alert(phone_number: str):
    """Unsubscribe from flood alerts"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM alert_subscriptions WHERE phone_number=$1", phone_number)
        return {"message": "Unsubscribed successfully", "success": True}

@router.get("/subscribers")
async def get_subscribers():
    """Get all active subscribers (admin use)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT phone_number, location_name, risk_threshold FROM alert_subscriptions")
        return {"count": len(rows), "subscribers": [dict(r) for r in rows]}
