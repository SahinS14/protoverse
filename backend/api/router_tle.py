from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from service.tle_service import tle_service

router = APIRouter(prefix="/tle", tags=["TLE Data"])


class SatelliteSchema(BaseModel):
    id: int
    sat_name: str
    epoch: Optional[str]
    source: Optional[str]


class TLEUpdateResponse(BaseModel):
    message: str
    count: int


@router.post("/refresh", response_model=TLEUpdateResponse)
async def refresh_tles():
    """Fetches TLE data from Celestrak and updates the database."""
    try:
        count = tle_service.update_tles_from_source()
        return {"message": "TLE data successfully loaded", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/list", response_model=List[SatelliteSchema])
async def list_satellites(limit: int = 100, country: str = None, priority: str = None):
    """Lists the satellites in the system. Supports country and priority filters."""
    return tle_service.get_all_satellites(limit, country=country, priority=priority)


@router.get("/count")
async def get_satellite_count():
    """Returns the total number of satellites."""
    count = tle_service.get_total_count()
    return {"count": count}


@router.get("/search", response_model=List[SatelliteSchema])
async def search_satellites(q: str = Query(..., min_length=2)):
    """Searches satellites by name."""
    results = tle_service.search_satellites(q)
    return results


 # --- This ID endpoint should be at the end
 # --- If placed above, it may catch the "/count" request as an ID and cause an error
@router.get("/{sat_id}")
async def get_satellite_details(sat_id: int):
    """Returns the raw TLE data by ID."""
    sat = tle_service.get_satellite_by_id(sat_id)
    if not sat:
        raise HTTPException(status_code=404, detail="Satellite not found")
    return sat
