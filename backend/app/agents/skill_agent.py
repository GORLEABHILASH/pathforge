import anthropic
from app.models.profile import ExtractedProfile, OnboardingInput, CompanyTarget
from app.models.skills import SkillRoadmapResponse, SkillDemand, SkillRoadmapItem, LearningStep

client = anthropic.Anthropic()

ROADMAP_TOOL = {
    "name": "generate_skill_roadmap",
    "description": (
        "Generate a brutally honest skill demand analysis and personalized learning roadmap. "
        "Base demand numbers on real 2024-2025 market data. Do not inflate. Do not encourage. State facts."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "top_market_skills": {
                "type": "array",
                "description": "Top 10 most in-demand skills for this candidate's target role and market right now",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill": {"type": "string"},
                        "demand_score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "trend": {"type": "string", "enum": ["exploding", "growing", "stable", "declining"]},
                        "trend_pct": {"type": "integer", "description": "YoY % change in job postings requiring this skill"},
                        "job_count_estimate": {"type": "integer", "description": "Approximate US job postings requiring this skill"},
                        "hire_probability_boost": {"type": "integer", "description": "Percentage points added to hire probability if candidate has this skill"}
                    },
                    "required": ["skill", "demand_score", "trend", "trend_pct", "job_count_estimate", "hire_probability_boost"]
                }
            },
            "your_gaps": {
                "type": "array",
                "description": "Personalized roadmap for the candidate's top 4-5 gaps that most impact their hire probability",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill": {"type": "string"},
                        "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                        "current_level": {"type": "string", "enum": ["none", "beginner", "intermediate"]},
                        "target_level": {"type": "string", "enum": ["working", "proficient", "expert"]},
                        "why_it_matters": {
                            "type": "string",
                            "description": "One honest sentence: why this specific gap is costing them interviews"
                        },
                        "hire_probability_boost": {"type": "integer"},
                        "steps": {
                            "type": "array",
                            "description": "3-5 concrete sequential steps to close this gap",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "order": {"type": "integer"},
                                    "what": {"type": "string", "description": "Exactly what to learn or do"},
                                    "how": {"type": "string", "description": "Specific resource, course, or approach (name it exactly)"},
                                    "time_estimate": {"type": "string"},
                                    "deliverable": {"type": "string", "description": "Concrete thing to build or produce as proof"}
                                },
                                "required": ["order", "what", "how", "time_estimate", "deliverable"]
                            }
                        }
                    },
                    "required": ["skill", "priority", "current_level", "target_level", "why_it_matters", "hire_probability_boost", "steps"]
                }
            },
            "total_weeks_to_ready": {
                "type": "integer",
                "description": "Honest estimate of weeks to be interview-ready if candidate follows the roadmap at their available hours/week"
            },
            "current_hire_probability": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Current probability of getting hired at target companies within 90 days"
            },
            "projected_hire_probability": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Probability after completing the roadmap"
            }
        },
        "required": [
            "top_market_skills", "your_gaps", "total_weeks_to_ready",
            "current_hire_probability", "projected_hire_probability"
        ]
    }
}

TARGET_CONTEXT = {
    CompanyTarget.faang: "FAANG/Top Tier (Google, Meta, Amazon, Apple, Microsoft, OpenAI). Requires LeetCode hard, system design mastery, measurable impact.",
    CompanyTarget.high_growth: "High Growth Tech (Stripe, Airbnb, Figma, Notion, Linear). Strong fundamentals + shipped products + clear ownership.",
    CompanyTarget.any_tech: "Any established tech company. Solid fundamentals, working portfolio, good communication.",
    CompanyTarget.any_company: "Any organization. Core programming skills and professionalism.",
    CompanyTarget.specific: "Specific target companies chosen by user.",
}


async def generate_skill_roadmap(
    profile: ExtractedProfile,
    onboarding: OnboardingInput,
) -> SkillRoadmapResponse:
    skills_str = ", ".join(profile.skills)
    gaps_str = "\n".join(f"- {g}" for g in profile.top_gaps)
    target_ctx = TARGET_CONTEXT.get(onboarding.target, "")
    projects_str = "\n".join(
        f"- {p.name}: {p.description} (stack: {', '.join(p.tech_stack)})"
        for p in profile.projects
    ) or "None listed"

    prompt = f"""You are PathForge's skill intelligence agent. Generate a brutally honest skill demand analysis and learning roadmap.

CRITICAL RULES:
- Use REAL 2024-2025 market data for skill demand numbers. Do not make up optimistic numbers.
- Be specific in learning steps. "Take a course" is useless. Name the exact course or resource.
- Deliverables must be specific projects, not vague outcomes.
- Hire probability boosts must be realistic. Getting good at Python doesn't add 40%.
- Total weeks to ready must account for the candidate's available hours/week.

CANDIDATE:
Name: {profile.name}
Current Skills: {skills_str}
Employability Score: {profile.employability_score}/100
Visa: {onboarding.visa_status}
Target: {onboarding.target} — {target_ctx}
Available: {onboarding.hours_per_week} hours/week
Goal: {onboarding.goal}

WHAT THEY BUILT:
{projects_str}

THEIR IDENTIFIED GAPS:
{gaps_str}

Generate:
1. Top 10 skills in demand RIGHT NOW for their target role (mix of skills they have and don't have — show the full market picture)
2. Personalized roadmap for their top 4-5 gaps that would most increase their hire probability
3. Honest timeline based on {onboarding.hours_per_week} hours/week

Use the generate_skill_roadmap tool."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=[ROADMAP_TOOL],
        tool_choice={"type": "tool", "name": "generate_skill_roadmap"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    d = tool_use.input

    return SkillRoadmapResponse(
        top_market_skills=[SkillDemand(**s) for s in d["top_market_skills"]],
        your_gaps=[
            SkillRoadmapItem(
                **{k: v for k, v in gap.items() if k != "steps"},
                steps=[LearningStep(**s) for s in gap["steps"]],
            )
            for gap in d["your_gaps"]
        ],
        total_weeks_to_ready=d["total_weeks_to_ready"],
        current_hire_probability=d["current_hire_probability"],
        projected_hire_probability=d["projected_hire_probability"],
    )
