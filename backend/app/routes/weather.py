from fastapi import APIRouter, Query
from app.services.weather_service import get_weather_by_coords, get_weather_by_city

router = APIRouter()

@router.get("/current")
async def current_weather(lat: float = Query(...), lon: float = Query(...)):
    """Get current weather for given coordinates"""
    return await get_weather_by_coords(lat, lon)

@router.get("/city")
async def city_weather(city: str = Query(...)):
    """Get current weather for a city name"""
    return await get_weather_by_city(city)
