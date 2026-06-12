from fastapi import APIRouter, Query, Request
from app.models.flood_predictor import predict_flood_risk
from app.services.river_service import get_river_level
from app.limiter import limiter

router = APIRouter()

@router.get("/predict")
@limiter.limit("30/minute")
async def predict_risk(
    request: Request,
    lat: float = Query(...),
    lon: float = Query(...),
    rainfall: float = Query(0),
    humidity: float = Query(70),
    temperature: float = Query(28),
    wind_speed: float = Query(10),
    river_level: float = Query(0),     # caller can pass a known value
    location_name: str = Query("")
):
    """
    Predict flood risk for given location and weather inputs.
    Automatically fetches real river discharge from GloFAS (Open-Meteo)
    if river_level is not provided (defaults to 0).
    """
    # --- Fetch real river level if not supplied ---
    river_data = {"river_level": river_level, "discharge_m3s": None, "source": "caller"}
    if river_level == 0:
        river_data = await get_river_level(lat, lon)
        river_level = river_data["river_level"]

    result = predict_flood_risk(
        rainfall=rainfall,
        humidity=humidity,
        temperature=temperature,
        wind_speed=wind_speed,
        river_level=river_level,
        lat=lat,
        lon=lon,
        location_name=location_name
    )

    # Attach river metadata to the response for transparency
    result["river_discharge_m3s"]  = river_data.get("discharge_m3s")
    result["river_data_source"]    = river_data.get("source", "proxy")

    return result
