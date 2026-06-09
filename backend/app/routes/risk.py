from fastapi import APIRouter, Query
from app.models.flood_predictor import predict_flood_risk

router = APIRouter()

@router.get("/predict")
async def predict_risk(
    lat: float = Query(...),
    lon: float = Query(...),
    rainfall: float = Query(0),
    humidity: float = Query(70),
    temperature: float = Query(28),
    wind_speed: float = Query(10),
    river_level: float = Query(0)
):
    """Predict flood risk for given location and weather inputs"""
    result = predict_flood_risk(
        rainfall=rainfall,
        humidity=humidity,
        temperature=temperature,
        wind_speed=wind_speed,
        river_level=river_level,
        lat=lat,
        lon=lon
    )
    return result
