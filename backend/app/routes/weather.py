from fastapi import APIRouter, Query, Request
from app.services.weather_service import get_weather_by_coords, get_weather_by_city
from app.main import limiter

router = APIRouter()

@router.get("/current")
@limiter.limit("30/minute")
async def current_weather(request: Request, lat: float = Query(...), lon: float = Query(...)):
    """Get current weather for given coordinates — rate limited to 30/min per IP"""
    return await get_weather_by_coords(lat, lon)

@router.get("/city")
@limiter.limit("30/minute")
async def city_weather(request: Request, city: str = Query(...)):
    """Get current weather for a city name — rate limited to 30/min per IP"""
    return await get_weather_by_city(city)
