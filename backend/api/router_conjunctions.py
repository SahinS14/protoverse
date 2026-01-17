from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from service.conjunction_service import conjunction_service

router = APIRouter(prefix="/conjunctions", tags=["Conjunction Analysis"])


class ConjunctionAlertSchema(BaseModel):
    """
    Schema for representing a conjunction alert event between two satellites.
    Includes satellite IDs, names, time of closest approach, miss distance, relative velocity, score, and event type.
    """
    id: int
    sat1_id: int
    sat1_name: str
    sat2_id: int
    sat2_name: str
    tca: str
    miss_distance_km: float
    rel_velocity_km_s: float
    score: float
    created_at: str
    event_type: str


class ScreeningResponse(BaseModel):
    """
    Response schema for the collision screening endpoint.
    Indicates the status, number of processed satellite pairs, and number of alerts saved.
    """
    status: str
    processed_pairs: int
    alerts_saved: int


@router.post("/run-screening", response_model=ScreeningResponse)
async def run_screening():
    """
    Manually triggers the collision screening process.
    This endpoint scans a 2-hour window starting from the current time and processes all satellite pairs for potential conjunctions.
    Returns the number of processed pairs and alerts saved.
    """
    try:
        result = conjunction_service.run_conjunction_screening()
        return {
            "status": "completed",
            "processed_pairs": result["processed_pairs"],
            "alerts_saved": result["alerts_saved"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/alerts", response_model=List[ConjunctionAlertSchema])
async def get_latest_alerts(limit: int = 20, type: str = "COLLISION", country: str = None, priority: str = None):
    """
    Retrieves the latest conjunction alerts from the database.
    Parameters:
        limit: Maximum number of alerts to return (default: 20)
        type: Type of event ('COLLISION' or 'DOCKING')
        country: Filter by country (e.g., 'India')
        priority: Filter by priority ('PRIMARY' or 'SECONDARY')
    Returns a list of conjunction alert events.
    """
    return conjunction_service.get_alerts(limit, event_type=type, country=country, priority=priority)
