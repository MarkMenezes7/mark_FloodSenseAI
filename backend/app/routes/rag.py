from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.models.rag_pipeline import get_rag_response
from app.main import limiter

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    current_risk_score: float | None = None

@router.post("/chat")
@limiter.limit("10/minute;100/day")
async def chat(request: Request, body: ChatRequest):
    """RAG-powered flood assistant chat endpoint — rate limited to 10/min, 100/day per IP"""
    response = await get_rag_response(
        message=body.message,
        lat=body.latitude,
        lon=body.longitude,
        location_name=body.location_name,
        risk_score=body.current_risk_score
    )
    return {"response": response, "success": True}
