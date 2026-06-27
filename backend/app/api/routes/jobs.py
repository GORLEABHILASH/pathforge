from fastapi import APIRouter, HTTPException
from app.models.jobs import JobMatchRequest, JobMatchResponse
from app.agents.job_agent import match_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/match", response_model=JobMatchResponse)
async def match_jobs_endpoint(request: JobMatchRequest):
    try:
        jobs, total_fetched, total_after_filter, used_stub = await match_jobs(
            request.profile, request.onboarding
        )
        return JobMatchResponse(
            jobs=jobs,
            total_fetched=total_fetched,
            total_after_visa_filter=total_after_filter,
            used_stub=used_stub,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job matching failed: {str(e)}")
