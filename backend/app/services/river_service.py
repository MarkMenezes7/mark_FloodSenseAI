"""
river_service.py — Real river discharge data from Open-Meteo Flood API
Source: https://flood-api.open-meteo.com (GloFAS v4 model, updated daily)
No API key required. Completely free.

Returns river_level on a 0-10 scale (compatible with flood_predictor.py)
based on actual river discharge in m³/s.
"""

import httpx
from functools import lru_cache
from datetime import datetime

FLOOD_API = "https://flood-api.open-meteo.com/v1/flood"


async def get_river_level(lat: float, lon: float) -> dict:
    """
    Fetch real river discharge for given coordinates from the Open-Meteo
    GloFAS flood API, and return a normalised 0-10 river_level score.

    GloFAS discharge percentile thresholds (global median river behaviour):
    - < 50 m³/s  → Low / normal flow
    - 50-200      → Rising / elevated
    - 200-500     → High — potential flooding
    - 500-1000    → Severe flooding risk
    - > 1000      → Extreme / major flood event

    These are broad global thresholds. For India's major rivers (Ganga, Brahmaputra)
    the actual flood thresholds are much higher, but the 0-10 scale normalisation
    still correctly shows relative urgency.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(FLOOD_API, params={
                "latitude": lat,
                "longitude": lon,
                "daily": "river_discharge",
                "past_days": 2,        # today + yesterday — gives trend context
                "forecast_days": 1,    # today's forecast
            })
            data = resp.json()

        if "daily" not in data or "river_discharge" not in data["daily"]:
            return {"river_level": 0, "discharge_m3s": None, "source": "unavailable"}

        discharge_values = [v for v in data["daily"]["river_discharge"] if v is not None]
        if not discharge_values:
            return {"river_level": 0, "discharge_m3s": None, "source": "unavailable"}

        # Use the maximum discharge in the window (past 2 days + today)
        # This captures already-elevated river conditions that will cause flooding
        discharge = max(discharge_values)
        current_discharge = discharge_values[-1]  # today's forecast value

        # Normalise to 0-10 scale (global scale — covers all rivers worldwide)
        if discharge >= 2000:   level = 10.0
        elif discharge >= 1000: level = 8.0 + (discharge - 1000) / 500
        elif discharge >= 500:  level = 6.0 + (discharge - 500) / 250
        elif discharge >= 200:  level = 4.0 + (discharge - 200) / 150
        elif discharge >= 100:  level = 2.5 + (discharge - 100) / 67
        elif discharge >= 50:   level = 1.0 + (discharge - 50) / 33
        elif discharge >= 10:   level = 0.2 + (discharge - 10) / 25
        else:                   level = 0.0

        level = round(min(max(level, 0.0), 10.0), 2)

        return {
            "river_level": level,
            "discharge_m3s": round(current_discharge, 1),
            "peak_discharge_m3s": round(discharge, 1),
            "source": "GloFAS via Open-Meteo",
            "dates": data["daily"].get("time", [])
        }

    except Exception as e:
        print(f"[RiverService] Open-Meteo flood API error: {e}")
        return {"river_level": 0, "discharge_m3s": None, "source": "error"}
