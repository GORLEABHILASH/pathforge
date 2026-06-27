# PathForge

> No hardworking, skilled engineer should ever be unemployed.

PathForge is a career intelligence platform that helps international students and skilled engineers get employed. It combines AI-powered job matching, honest skill assessment, warm introduction mapping, and tailored resume generation into one focused platform.

## Mission

If you are willing to learn, willing to grow, and willing to put in the effort — PathForge will make sure your skills find their place in the world.

## What PathForge Does

- **Honest Employability Score** — Know exactly where you stand. No inflation. No false hope.
- **Skill Demand Intelligence** — Real-time data on which skills are in demand and the exact impact on your hiring probability.
- **Job Matching with Visa Filter** — Only jobs from companies that sponsor visas, ranked by relevance to your actual experience.
- **Product DNA Matching** — Matches what you have *built* to companies building similar products, not just skill keywords.
- **Warm Introduction Engine** — Maps your existing network to target companies and generates exact outreach messages.
- **Tailored Resume Generator** — A different, ATS-optimized resume for every job. Generated in seconds.
- **Application Quality Gate** — Stops bad applications before they happen.
- **Interview Preparation** — Company-specific prep with honest AI scoring.
- **Candidate Validation** — Verified badges employers trust.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + Tailwind CSS |
| Backend | Python FastAPI |
| AI | Claude API (claude-sonnet-4-6) |
| Database | Supabase (PostgreSQL) |
| Cache | Redis |
| Job Data | JSearch API + Adzuna API |
| Visa Data | USCIS H1B Database |
| Payments | Stripe |
| Deployment | Vercel + Railway |

## Project Structure

```
pathforge/
├── frontend/          # Next.js 14 application
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── agents/    # AI agents (Claude)
│   │   ├── models/    # Database models
│   │   └── services/  # Business logic
└── docs/              # Architecture and product docs
```

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Core Principle

PathForge is brutally honest. It will not tell you what you want to hear. It will tell you what you need to hear — and exactly what to do about it.

*"We would rather make you uncomfortable today than unemployed tomorrow."*

---

Built for international students. Built for hardworking engineers. Built to get people hired.
