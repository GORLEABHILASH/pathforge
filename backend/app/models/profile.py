from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class VisaStatus(str, Enum):
    f1 = "F-1 Student"
    opt = "OPT"
    stem_opt = "STEM OPT"
    h1b = "H-1B"
    green_card = "Green Card"
    citizen = "US Citizen"
    other = "Other"


class CompanyTarget(str, Enum):
    faang = "FAANG / Top Tier"
    high_growth = "High Growth Tech"
    any_tech = "Any Tech Company"
    any_company = "Just Get Employed"
    specific = "Specific Companies"


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str
    impact: Optional[str] = None


class Project(BaseModel):
    name: str
    description: str
    tech_stack: list[str]
    impact: Optional[str] = None
    url: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: Optional[str] = None
    gpa: Optional[float] = None


class EmployabilityBreakdown(BaseModel):
    skills_breadth: int = Field(ge=0, le=25, description="Skills variety and relevance")
    experience_quality: int = Field(ge=0, le=25, description="Quality of work experience and impact")
    project_strength: int = Field(ge=0, le=20, description="Portfolio projects quality")
    education: int = Field(ge=0, le=15, description="Education relevance")
    market_alignment: int = Field(ge=0, le=15, description="How well skills match current market demand")


class ExtractedProfile(BaseModel):
    name: str
    skills: list[str]
    experience: list[Experience]
    projects: list[Project]
    education: list[Education]
    employability_score: int = Field(ge=0, le=100)
    breakdown: EmployabilityBreakdown
    honest_assessment: str
    top_gaps: list[str]
    immediate_actions: list[str]


class OnboardingInput(BaseModel):
    resume_text: str
    visa_status: VisaStatus
    target: CompanyTarget
    specific_companies: Optional[list[str]] = None
    hours_per_week: int = Field(ge=1, le=80)
    goal: str


class ProfileCreateRequest(BaseModel):
    onboarding: OnboardingInput
    email: str


class ProfileResponse(BaseModel):
    profile: ExtractedProfile
    onboarding: OnboardingInput
    email: str
