from fastapi import APIRouter
from pydantic import BaseModel
from app.models.rag_pipeline import get_rag_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    current_risk_score: float | None = None

@router.post("/chat")
async def chat(request: ChatRequest):
    """RAG-powered flood assistant chat endpoint"""
    response = await get_rag_response(
        message=request.message,
        lat=request.latitude,
        lon=request.longitude,
        location_name=request.location_name,
        risk_score=request.current_risk_score
    )
    return {"response": response, "success": True}
