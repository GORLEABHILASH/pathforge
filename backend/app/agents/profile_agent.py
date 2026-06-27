import json
import anthropic
from app.models.profile import (
    ExtractedProfile,
    EmployabilityBreakdown,
    Experience,
    Project,
    Education,
    OnboardingInput,
    CompanyTarget,
)

client = anthropic.Anthropic()

EXTRACTION_TOOL = {
    "name": "extract_profile",
    "description": "Extract structured profile data from resume and onboarding inputs. Be brutally honest in assessments — no inflation, no false hope.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Technical skills extracted from resume"
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "role": {"type": "string"},
                        "duration": {"type": "string"},
                        "description": {"type": "string"},
                        "impact": {"type": "string"}
                    },
                    "required": ["company", "role", "duration", "description"]
                }
            },
            "projects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "tech_stack": {"type": "array", "items": {"type": "string"}},
                        "impact": {"type": "string"},
                        "url": {"type": "string"}
                    },
                    "required": ["name", "description", "tech_stack"]
                }
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "institution": {"type": "string"},
                        "degree": {"type": "string"},
                        "field": {"type": "string"},
                        "graduation_year": {"type": "string"},
                        "gpa": {"type": "number"}
                    },
                    "required": ["institution", "degree", "field"]
                }
            },
            "employability_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Honest score 0-100. Do not inflate. A score of 50 means average candidate, 70+ means competitive, 85+ means strong."
            },
            "breakdown": {
                "type": "object",
                "properties": {
                    "skills_breadth": {"type": "integer", "minimum": 0, "maximum": 25},
                    "experience_quality": {"type": "integer", "minimum": 0, "maximum": 25},
                    "project_strength": {"type": "integer", "minimum": 0, "maximum": 20},
                    "education": {"type": "integer", "minimum": 0, "maximum": 15},
                    "market_alignment": {"type": "integer", "minimum": 0, "maximum": 15}
                },
                "required": ["skills_breadth", "experience_quality", "project_strength", "education", "market_alignment"]
            },
            "honest_assessment": {
                "type": "string",
                "description": "2-4 sentences of brutally honest assessment. State exactly where the candidate stands, what is holding them back, and what the realistic outlook is. No encouragement fluff."
            },
            "top_gaps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top 3-5 specific gaps preventing them from getting hired at their target companies"
            },
            "immediate_actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top 3 specific, actionable things to do this week — ordered by impact"
            }
        },
        "required": [
            "name", "skills", "experience", "projects", "education",
            "employability_score", "breakdown", "honest_assessment",
            "top_gaps", "immediate_actions"
        ]
    }
}

TARGET_BENCHMARKS = {
    CompanyTarget.faang: "Google, Meta, Amazon, Apple, Microsoft, Netflix, OpenAI. These companies reject 98%+ of applicants. LeetCode hard proficiency, system design mastery, and measurable impact are required.",
    CompanyTarget.high_growth: "Stripe, Airbnb, Figma, Notion, Linear, Vercel, etc. High bar but more holistic. Strong fundamentals + real shipped products + clear ownership.",
    CompanyTarget.any_tech: "Any established tech company. Solid fundamentals, working portfolio, and good communication required.",
    CompanyTarget.any_company: "Any organization that pays. Core programming skills and professionalism required.",
    CompanyTarget.specific: "Specific target companies named by user.",
}


async def extract_profile(onboarding: OnboardingInput) -> ExtractedProfile:
    target_context = TARGET_BENCHMARKS.get(onboarding.target, "")
    specific = ""
    if onboarding.specific_companies:
        specific = f"Specific targets: {', '.join(onboarding.specific_companies)}."

    prompt = f"""You are PathForge's profile assessment agent. Your job is to extract structured data from this resume and give a BRUTALLY HONEST assessment.

CRITICAL RULES:
- Do NOT inflate the employability score. Most candidates score 30-60. Only truly exceptional candidates score 80+.
- Do NOT give empty encouragement. State facts.
- If their experience lacks measurable impact, say so.
- If their skills don't match their target, say so directly.
- Compare against REAL hiring bars, not idealized ones.

CANDIDATE CONTEXT:
- Visa Status: {onboarding.visa_status}
- Target: {onboarding.target} — {target_context} {specific}
- Hours available per week: {onboarding.hours_per_week}
- Goal: {onboarding.goal}

RESUME:
{onboarding.resume_text}

Extract the profile and give an honest assessment. Use the extract_profile tool."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_profile"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    data = tool_use.input

    breakdown = EmployabilityBreakdown(**data["breakdown"])

    return ExtractedProfile(
        name=data["name"],
        skills=data["skills"],
        experience=[Experience(**e) for e in data["experience"]],
        projects=[Project(**p) for p in data["projects"]],
        education=[Education(**e) for e in data["education"]],
        employability_score=data["employability_score"],
        breakdown=breakdown,
        honest_assessment=data["honest_assessment"],
        top_gaps=data["top_gaps"],
        immediate_actions=data["immediate_actions"],
    )
