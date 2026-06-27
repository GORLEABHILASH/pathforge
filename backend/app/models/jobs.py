from pydantic import BaseModel
from typing import Optional
from app.models.profile import ExtractedProfile, OnboardingInput


class RawJob(BaseModel):
    job_id: str
    job_title: str
    employer_name: str
    job_city: Optional[str] = None
    job_state: Optional[str] = None
    job_country: Optional[str] = None
    job_description: str
    job_apply_link: Optional[str] = None
    job_employment_type: Optional[str] = None
    job_is_remote: Optional[bool] = False


class MatchedJob(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    apply_link: Optional[str] = None
    is_remote: bool
    match_score: int
    visa_confidence: str  # "confirmed" | "likely" | "unknown" | "not_required"
    visa_signal: str
    why_match: str
    employment_type: Optional[str] = None


class JobMatchRequest(BaseModel):
    profile: ExtractedProfile
    onboarding: OnboardingInput


class JobMatchResponse(BaseModel):
    jobs: list[MatchedJob]
    total_fetched: int
    total_after_visa_filter: int
    used_stub: bool
