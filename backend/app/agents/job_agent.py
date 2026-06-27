import re
import anthropic
from app.models.profile import ExtractedProfile, OnboardingInput
from app.models.jobs import RawJob, MatchedJob
from app.services.jsearch_client import fetch_jobs
from app.services.visa_filter import filter_jobs

client = anthropic.Anthropic()

SCORING_TOOL = {
    "name": "score_jobs",
    "description": (
        "Score each job against the candidate profile. "
        "Focus on what the candidate has BUILT (projects, products) and WHERE they worked — "
        "not just skill keyword overlap."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                        "match_score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": (
                                "90-100: candidate's project/domain directly maps to this role. "
                                "70-89: strong alignment. "
                                "50-69: reasonable skill match, weak domain fit. "
                                "Below 50: mostly keyword overlap."
                            ),
                        },
                        "why_match": {
                            "type": "string",
                            "description": (
                                "One sentence. Must reference what the candidate built or "
                                "where they worked, not generic skills. "
                                "Example: 'Your fraud detection system maps directly to their "
                                "risk infrastructure team.'"
                            ),
                        },
                    },
                    "required": ["job_id", "match_score", "why_match"],
                },
            }
        },
        "required": ["scores"],
    },
}

_ROLE_KEYWORDS = [
    "software engineer", "software developer", "backend engineer", "frontend engineer",
    "full stack engineer", "fullstack engineer", "data engineer", "data scientist",
    "machine learning engineer", "ml engineer", "ai engineer", "platform engineer",
    "infrastructure engineer", "devops engineer", "site reliability engineer",
    "product engineer", "mobile engineer", "ios engineer", "android engineer",
    "security engineer", "cloud engineer",
]


def _extract_role_from_goal(goal: str) -> str:
    lower = goal.lower()
    for role in _ROLE_KEYWORDS:
        if role in lower:
            return role
    if "engineer" in lower:
        return "software engineer"
    if "data" in lower:
        return "data engineer"
    return "software engineer"


def _format_location(job: RawJob) -> str:
    if job.job_is_remote:
        return "Remote"
    parts = [p for p in [job.job_city, job.job_state] if p]
    return ", ".join(parts) if parts else (job.job_country or "Unknown")


def build_search_query(profile: ExtractedProfile, onboarding: OnboardingInput) -> str:
    role = _extract_role_from_goal(onboarding.goal)
    top_skills = " ".join(profile.skills[:3])
    return f"{role} {top_skills}".strip()


def _build_scoring_prompt(
    profile: ExtractedProfile,
    onboarding: OnboardingInput,
    jobs: list[tuple[RawJob, str, str]],
) -> str:
    skills_str = ", ".join(profile.skills[:15])

    projects_str = "\n".join(
        f"- {p.name}: {p.description} (stack: {', '.join(p.tech_stack)})"
        for p in profile.projects
    ) or "No projects listed"

    exp_str = "\n".join(
        f"- {e.role} at {e.company} ({e.duration}): {e.description}"
        for e in profile.experience
    ) or "No experience listed"

    jobs_str = "\n\n".join(
        f"JOB_ID: {job.job_id}\n"
        f"Title: {job.job_title}\n"
        f"Company: {job.employer_name}\n"
        f"Description: {job.job_description[:400]}"
        for job, _, _ in jobs
    )

    return f"""You are PathForge's job matching agent. Score each job 0-100 against this candidate.

CRITICAL RULE: Score based on what the candidate has BUILT and WORKED ON, not just skill keywords.
Product DNA matching: if a candidate built a payments system, score fintech roles higher.
If they built healthcare software, score health tech roles higher. Domain expertise > raw skills.

CANDIDATE:
Name: {profile.name}
Target: {onboarding.target}
Visa: {onboarding.visa_status}
Skills: {skills_str}

WHAT THEY BUILT (Projects):
{projects_str}

WHERE THEY WORKED (Experience):
{exp_str}

JOBS TO SCORE:
{jobs_str}

Score every single job. In why_match, write ONE sentence referencing what they built or where they worked.
Use the score_jobs tool."""


async def match_jobs(
    profile: ExtractedProfile,
    onboarding: OnboardingInput,
) -> tuple[list[MatchedJob], int, int, bool]:
    """Returns (matched_jobs, total_fetched, total_after_visa_filter, used_stub)."""
    query = build_search_query(profile, onboarding)
    raw_jobs, used_stub = await fetch_jobs(query)

    filtered = filter_jobs(raw_jobs, onboarding.visa_status)
    jobs_to_score = filtered[:20]

    if not jobs_to_score:
        return [], len(raw_jobs), 0, used_stub

    prompt = _build_scoring_prompt(profile, onboarding, jobs_to_score)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        tools=[SCORING_TOOL],
        tool_choice={"type": "tool", "name": "score_jobs"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    scores_by_id = {s["job_id"]: s for s in tool_use.input["scores"]}

    results: list[MatchedJob] = []
    for job, visa_confidence, visa_signal in jobs_to_score:
        score_data = scores_by_id.get(job.job_id, {})
        results.append(
            MatchedJob(
                job_id=job.job_id,
                title=job.job_title,
                company=job.employer_name,
                location=_format_location(job),
                apply_link=job.job_apply_link,
                is_remote=job.job_is_remote or False,
                match_score=score_data.get("match_score", 0),
                visa_confidence=visa_confidence,
                visa_signal=visa_signal,
                why_match=score_data.get("why_match", ""),
                employment_type=job.job_employment_type,
            )
        )

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results[:10], len(raw_jobs), len(filtered), used_stub
