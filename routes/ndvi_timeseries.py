from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from utils.sentinel import get_satellite_features  # You must define this or already have it

router = APIRouter()

class NDVITimeSeriesRequest(BaseModel):
    latitude: float
    longitude: float
    reference_date: str  # Format: YYYY-MM-DD

@router.post("/api/ndvi-timeseries")
async def compute_ndvi_timeseries(req: NDVITimeSeriesRequest):
    lat = req.latitude
    lon = req.longitude
    ref_date = datetime.strptime(req.reference_date, "%Y-%m-%d")
    start_date = ref_date - timedelta(weeks=52)

    results = []

    current_date = start_date
    while current_date <= ref_date:
        try:
            bands = get_satellite_features(lat, lon, current_date.strftime("%Y-%m-%d"))
            b08 = bands.get("B08")
            b04 = bands.get("B04")
            if b08 is not None and b04 is not None and (b08 + b04) != 0:
                ndvi = (b08 - b04) / (b08 + b04)
                results.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "ndvi": round(ndvi, 4)
                })
        except Exception as e:
            print(f"Error on {current_date.strftime('%Y-%m-%d')}: {e}")
        current_date += timedelta(days=7)

    return results
