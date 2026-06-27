# PathForge Architecture

## Core Modules (V1)

1. Honest profile assessment + employability score
2. Real-time skill demand intelligence + roadmap
3. Job matching with visa sponsorship filter
4. Product DNA matching
5. Warm introduction engine
6. Tailored resume generator per job
7. Application quality gate
8. Interview preparation + AI mock interviews
9. Candidate validation (Tier 1 + Tier 2)
10. Employer marketplace
11. Weekly accountability system
12. Human advisor touchpoints (premium)

## Agent Architecture

- Orchestrator Agent — coordinates all agents
- Profile Agent — parses resume, extracts skills
- Job Search Agent — finds relevant jobs
- Visa Filter Agent — cross-references H1B data
- Resume Agent — generates tailored resumes per job
- Skill Gap Agent — identifies gaps, creates roadmap
- Market Intelligence Agent — tracks skill demand
- Network Agent — finds warm introduction paths
- Interview Prep Agent — company-specific prep
- Assessment Agent — validates skills, assigns tier

## Data Sources

- JSearch API (LinkedIn + Indeed + Glassdoor aggregated)
- Adzuna API (global job listings)
- Greenhouse API (direct ATS feed)
- Lever API (direct ATS feed)
- USCIS H1B public database (visa sponsorship history)
- Web search (real-time market intelligence)

## Build Order

Week 1-2:  Onboarding + Profile system
Week 3-4:  Job matching + Visa filter
Week 5-6:  Resume generator agent
Week 7-8:  Employability score engine
Week 9-10: Employer portal + Tier system
Week 11-12: Interview prep + Feedback loop
