from fastapi import APIRouter, HTTPException
from app.models.skills import (
    SkillRoadmapRequest,
    SkillRoadmapResponse,
    ProgressUpdate,
    UserProgress,
)
from app.agents.skill_agent import generate_skill_roadmap
from app.services.supabase_client import get_client, is_available

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("/roadmap", response_model=SkillRoadmapResponse)
async def get_skill_roadmap(request: SkillRoadmapRequest):
    try:
        return await generate_skill_roadmap(request.profile, request.onboarding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill roadmap failed: {str(e)}")


@router.post("/progress")
async def save_progress(update: ProgressUpdate):
    if not is_available():
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        db = get_client()
        db.table("skill_progress").upsert(
            {
                "user_email": update.user_email,
                "skill": update.skill,
                "completed_steps": update.completed_steps,
                "notes": update.notes or "",
            },
            on_conflict="user_email,skill",
        ).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")


@router.get("/progress/{email}")
async def get_progress(email: str):
    if not is_available():
        return {"progress": [], "db_available": False}
    try:
        db = get_client()
        result = (
            db.table("skill_progress")
            .select("*")
            .eq("user_email", email)
            .execute()
        )
        return {"progress": result.data, "db_available": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")
