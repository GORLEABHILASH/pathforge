# PathForge — 2-Minute Demo Script

**Focus: How agents work, orchestration, and the loop**

---

## [0:00 – 0:15] The Hook

> "Most engineers apply to hundreds of jobs and hear nothing back. Not because they're bad — because they're competing blindly. PathForge fixes that with a 4-agent AI pipeline that gives you the honest career intelligence you actually need."

*Show the landing/onboarding screen.*

---

## [0:15 – 0:40] Profile Agent — The Main Agent

> "It starts with Agent 1 — the Profile Agent. You paste your resume, tell PathForge your target companies and goal, and submit."

*Paste resume text into the onboarding form. Hit Submit.*

> "Here's what makes this different from ChatGPT. Instead of asking Claude to just 'analyze my resume,' we use **forced tool use** — Claude is required to call a structured tool called `extract_profile`. It cannot return free-form text. It must produce a validated JSON object: employability score, 5-dimension breakdown, top gaps, immediate actions."

*Dashboard appears. Point to the score ring and breakdown bars.*

> "This profile object — this structured data — is the master signal. Every other agent downstream receives it."

---

## [0:40 – 1:00] Job Agent — Specialist Agent with Product DNA

> "Agent 2 is the Job Agent. It takes that profile, fetches real job listings, and calls Claude again — this time forced to call `score_jobs`."

*Scroll to the Matched Jobs section.*

> "The key here is **Product DNA matching**. We don't score on skill keywords. Claude looks at what you actually *built* — your projects, your domain — and maps that to what each company is building. If you built a payments system, fintech roles score higher. If you built healthcare software, health tech roles score higher."

*Point to a job card with a `why_match` quote.*

> "Every match comes with one honest sentence explaining exactly why it fits — not a keyword score, a domain explanation."

---

## [1:00 – 1:25] Skill Agent — The Loop

> "Agent 3 is where the loop begins. Click 'Learning Roadmap.'"

*Navigate to /skills.*

> "The Skill Agent calls Claude with another forced tool — `generate_skill_roadmap`. It takes the profile's gaps and produces: top 10 in-demand skills with real market data, and a personalized step-by-step roadmap for each gap."

*Point to the hire probability banner: "32% → 61%".*

> "But here's the agentic loop. The candidate checks off steps as they complete them."

*Click a checkbox on a learning step.*

> "That saves to Supabase instantly. As the candidate levels up, they re-run their profile assessment. The new profile feeds fresher data into every downstream agent — better job matches, better introductions. The loop runs until they're hired."

---

## [1:25 – 1:45] Network Agent — Warm Introductions

> "Agent 4 — the Network Agent. Click 'Warm Introductions.' Upload your LinkedIn Connections CSV."

*Drag and drop a CSV file onto the upload zone.*

> "The agent pre-filters hundreds of connections down to the 30 most relevant — FAANG first, then high-growth companies, then top employers. Then it calls Claude with `generate_outreach` — forced tool use again — and produces a personalized message for each connection: relevance score, why they matter, a subject line, and a message under 120 words with one clear ask."

*Expand an outreach card. Show subject + message.*

> "Connections at companies from the Job Agent results get flagged 'Actively Hiring.' Hit Copy, send it on LinkedIn. Done."

---

## [1:45 – 2:00] Architecture Summary + Close

> "So the full pipeline:"

*Narrate the architecture:*

> "**Orchestration**: the backend sequences all four agents. Each one uses Claude with forced tool use — structured JSON in, structured JSON out, no hallucinated formats.
>
> **The main agent** — Profile Agent — generates the master profile that every specialist agent consumes.
>
> **The loop** — Skill progress feeds back into profile reassessment, which updates job matches and network relevance — continuously, until the candidate gets hired.
>
> This is PathForge. Four agents. One loop. No fluff."

---

## Key Lines to Memorize

- *"Forced tool use means Claude cannot return free-form text — it must produce structured output our pipeline can pass to the next agent."*
- *"Product DNA matching: we score what you built, not what keywords you listed."*
- *"The loop runs until they're hired."*
