from pydantic import BaseModel
from typing import Optional
from app.models.profile import ExtractedProfile, OnboardingInput


class SkillDemand(BaseModel):
    skill: str
    demand_score: int          # 0-100, how hot this skill is in the market
    trend: str                 # "exploding" | "growing" | "stable" | "declining"
    trend_pct: int             # e.g. +340 means +340% growth in job postings
    job_count_estimate: int    # approx jobs requiring this skill
    hire_probability_boost: int  # percentage points added to hire probability if learned


class LearningStep(BaseModel):
    order: int
    what: str        # what to learn / do
    how: str         # specific resource or approach
    time_estimate: str  # e.g. "2 weeks", "1 month"
    deliverable: str    # concrete thing to build or produce


class SkillRoadmapItem(BaseModel):
    skill: str
    priority: int               # 1 = highest
    current_level: str          # "none" | "beginner" | "intermediate"
    target_level: str           # "working" | "proficient" | "expert"
    why_it_matters: str         # one sentence — honest, not fluffy
    hire_probability_boost: int
    steps: list[LearningStep]


class SkillRoadmapResponse(BaseModel):
    top_market_skills: list[SkillDemand]   # top 10 skills in demand for their target
    your_gaps: list[SkillRoadmapItem]      # personalized roadmap for their specific gaps
    total_weeks_to_ready: int              # honest estimate to be interview-ready
    current_hire_probability: int          # 0-100
    projected_hire_probability: int        # after completing roadmap


class SkillRoadmapRequest(BaseModel):
    profile: ExtractedProfile
    onboarding: OnboardingInput


class ProgressUpdate(BaseModel):
    user_email: str
    skill: str
    completed_steps: list[int]   # list of step order numbers completed
    notes: Optional[str] = None


class UserProgress(BaseModel):
    user_email: str
    skill: str
    completed_steps: list[int]
    notes: Optional[str] = None
    updated_at: Optional[str] = None
