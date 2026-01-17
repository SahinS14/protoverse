from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.db import get_conn

router = APIRouter(prefix="/mission", tags=["Critical Mission Mode"])

class MissionRequest(BaseModel):
    region: str
    reason: str

mission_context = {"status": "deactivated", "region": None, "reason": None}

@router.post("/activate")
async def activate_mission(req: MissionRequest):
    # Mock logic: Mark all satellites as CRITICAL
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE raw_tles SET mission_priority = 'CRITICAL'")
        conn.commit()
        conn.close()
        mission_context["status"] = "activated"
        mission_context["region"] = req.region
        mission_context["reason"] = req.reason
        return {"status": "activated", "region": req.region, "reason": req.reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate")
async def deactivate_mission():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE raw_tles SET mission_priority = 'NORMAL'")
        conn.commit()
        conn.close()
        mission_context["status"] = "deactivated"
        mission_context["region"] = None
        mission_context["reason"] = None
        return {"status": "deactivated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context")
async def get_mission_context():
    return mission_context
