# PathForge — Hackathon Concept Brief

**"No hardworking, skilled engineer should ever be unemployed."**

---

## The Problem

Engineers spend hundreds of hours applying to jobs that never respond — not because they aren't good enough, but because they compete blindly: wrong companies, wrong positioning, no warm connections, no idea what's actually holding them back. 70% of jobs are filled through referrals. Most candidates have zero framework to compete intelligently.

---

## What PathForge Does

PathForge is a career intelligence platform powered by a 4-agent AI pipeline. You paste your resume once. Four specialized agents run in sequence to give you the complete picture: where you honestly stand, which jobs you actually match, what to learn next, and who in your network can get you in the door.

**No fluff. No encouragement. Brutally honest, actionable intelligence.**

---

## Agent Architecture

PathForge is built on a **4-agent pipeline** where each agent's output feeds the next.

### Agent 1 — Profile Agent (Main Agent / Orchestrator Signal)
The entry point. Takes resume text + target companies + career goal → calls Claude with **forced tool use** (`tool_choice: "extract_profile"`) to produce a structured, honest profile: employability score (0–100), skill breakdown across 5 dimensions, top gaps, and immediate actions. This profile object is the master signal passed to every downstream agent.

### Agent 2 — Job Agent (Specialist)
Takes the structured profile → fetches real remote jobs from the Jobicy API → passes all jobs + profile to Claude in a single call using **forced tool use** (`tool_choice: "score_jobs"`). Claude scores every job on **Product DNA matching** — not just skill keywords but what the candidate actually *built*. Returns top 10 ranked matches with honest explanations.

### Agent 3 — Skill Agent (Specialist + Loop)
Takes the profile + identified gaps → calls Claude with **forced tool use** (`tool_choice: "generate_skill_roadmap"`) to generate a week-by-week learning plan: top 10 in-demand skills with real market data, 4–5 personalized gap roadmaps with specific steps and deliverables, and honest hire probability before and after. The user checks off completed steps → progress saves to Supabase → the loop runs continuously as the candidate levels up. **This is the agentic loop**: each profile re-assessment produces updated recommendations based on new progress.

### Agent 4 — Network Agent (Specialist)
Takes the structured profile + job match companies + LinkedIn Connections CSV → pre-filters to the 30 most relevant connections (FAANG > high-growth > top employers) → calls Claude with **forced tool use** (`tool_choice: "generate_outreach"`) to score each connection and write a personalized, non-template outreach message under 120 words with a single clear ask. Marks companies from Job Agent results as "Actively Hiring."

---

## Why Forced Tool Use Matters

Every agent uses `tool_choice: {"type": "tool", "name": "..."}` — Claude is **forced** to call the tool and return structured JSON. No free-form text, no hallucinated format. This means the output is always parseable, the schema is always enforced, and each agent's output is safe to pass directly into the next agent's input. This is what makes the pipeline reliable.

---

## The Agentic Loop

```
Resume → [Profile Agent] → master profile
                              ↓
              ┌─────────────────────────────────┐
              │ [Job Agent]  → ranked job list  │
              │ [Skill Agent] → learning roadmap│  ← user checks steps
              │ [Network Agent] → outreach msgs │     ↓ progress saved
              └─────────────────────────────────┘   re-assess profile
                                                      ↓ loop continues
```

The candidate marks learning steps complete → profile score improves → job matches update → better introductions become available. The loop runs until they're hired.

---

## Tech Stack

- **Backend**: FastAPI (Python) + Anthropic SDK (`claude-sonnet-4-6`)
- **Frontend**: Next.js 16 + Tailwind CSS
- **Database**: Supabase (PostgreSQL) — persists profiles, progress, job history
- **Job Data**: Jobicy API (free, real remote tech jobs)

---

## Who It's For

Any engineer — new grad, career switcher, or experienced professional — who is skilled and hardworking but losing to the job search system, not to better candidates.
