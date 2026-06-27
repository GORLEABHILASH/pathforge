import os
import re
import httpx
from app.models.jobs import RawJob

_HTML_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    return _WHITESPACE.sub(" ", _HTML_TAG.sub(" ", text)).strip()


def _map_jobicy(j: dict, index: int) -> RawJob:
    geo = j.get("jobGeo", "Remote")
    description = _strip_html(j.get("jobDescription", j.get("jobExcerpt", "")))
    return RawJob(
        job_id=f"jobicy-{j.get('id', index)}",
        job_title=j.get("jobTitle", ""),
        employer_name=j.get("companyName", ""),
        job_city=None,
        job_state=geo if geo not in ("USA", "Worldwide", "LATAM", "Europe") else None,
        job_country="US",
        job_description=description,
        job_apply_link=j.get("url"),
        job_employment_type=(j.get("jobType") or ["FULLTIME"])[0].upper().replace("-", ""),
        job_is_remote=True,
    )

STUB_JOBS: list[RawJob] = [
    RawJob(
        job_id="stub-001",
        job_title="Software Engineer, Backend",
        employer_name="Stripe",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="We are hiring a backend engineer to work on our payments infrastructure. Experience with Python, distributed systems, and APIs required. We sponsor H-1B visas and provide full immigration support for qualified candidates.",
        job_apply_link="https://stripe.com/jobs",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-002",
        job_title="Machine Learning Engineer",
        employer_name="Google",
        job_city="Mountain View", job_state="CA", job_country="US",
        job_description="Join Google Brain to build the next generation of ML systems. Strong Python, TensorFlow/PyTorch, and ML fundamentals required. Google supports H-1B sponsorship and OPT authorization for all engineering roles.",
        job_apply_link="https://careers.google.com",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-003",
        job_title="Full Stack Engineer",
        employer_name="Notion",
        job_city="New York", job_state="NY", job_country="US",
        job_description="Build the collaboration tools used by millions. We're looking for engineers who care deeply about product. TypeScript, React, Node.js. We are willing to sponsor work authorization for exceptional candidates.",
        job_apply_link="https://notion.so/jobs",
        job_employment_type="FULLTIME",
        job_is_remote=True,
    ),
    RawJob(
        job_id="stub-004",
        job_title="Data Engineer",
        employer_name="Databricks",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="Build the data lakehouse. Experience with Spark, Python, SQL, and distributed data systems required. Databricks sponsors H-1B visas and offers comprehensive immigration support.",
        job_apply_link="https://databricks.com/company/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-005",
        job_title="Software Engineer",
        employer_name="Coinbase",
        job_city="Remote", job_state=None, job_country="US",
        job_description="Build the infrastructure for the open financial system. Go, Python, distributed systems. We value builders who ship. Must be authorized to work in the US — we do not offer visa sponsorship at this time.",
        job_apply_link="https://coinbase.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=True,
    ),
    RawJob(
        job_id="stub-006",
        job_title="Backend Engineer",
        employer_name="Airbnb",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="Scale systems that power global travel. Java, Python, microservices. Airbnb provides H-1B sponsorship and OPT support for all engineers.",
        job_apply_link="https://careers.airbnb.com",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-007",
        job_title="Software Development Engineer",
        employer_name="Amazon",
        job_city="Seattle", job_state="WA", job_country="US",
        job_description="Build services at scale on AWS. Java, Python, distributed systems experience. Amazon is one of the largest H-1B sponsors in the United States and supports work authorization for all positions.",
        job_apply_link="https://amazon.jobs",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-008",
        job_title="Frontend Engineer",
        employer_name="Figma",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="Make design tools that designers love. React, TypeScript, WebGL, performance engineering. Figma sponsors visa applications for candidates who require work authorization.",
        job_apply_link="https://figma.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-009",
        job_title="Platform Engineer",
        employer_name="Vercel",
        job_city="Remote", job_state=None, job_country="US",
        job_description="Build the infrastructure that powers the modern web. Kubernetes, Rust, Go, distributed systems. This role requires existing authorization to work in the United States.",
        job_apply_link="https://vercel.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=True,
    ),
    RawJob(
        job_id="stub-010",
        job_title="Software Engineer, Infrastructure",
        employer_name="Meta",
        job_city="Menlo Park", job_state="CA", job_country="US",
        job_description="Scale the infrastructure serving billions of users. C++, Python, distributed systems, performance optimization. Meta sponsors H-1B petitions and provides immigration support services.",
        job_apply_link="https://metacareers.com",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-011",
        job_title="Senior Software Engineer",
        employer_name="Snowflake",
        job_city="San Mateo", job_state="CA", job_country="US",
        job_description="Build the cloud data platform. Java, C++, distributed databases. Snowflake supports H-1B sponsorship for engineering roles.",
        job_apply_link="https://snowflake.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-012",
        job_title="Product Engineer",
        employer_name="Linear",
        job_city="Remote", job_state=None, job_country="US",
        job_description="Build the issue tracker that engineering teams love. TypeScript, React, GraphQL, Postgres. Small team, high ownership. We do not currently sponsor new visa applications.",
        job_apply_link="https://linear.app/careers",
        job_employment_type="FULLTIME",
        job_is_remote=True,
    ),
    RawJob(
        job_id="stub-013",
        job_title="Software Engineer",
        employer_name="Palantir Technologies",
        job_city="New York", job_state="NY", job_country="US",
        job_description="Build data platforms for mission-critical decisions. Java, Python, distributed systems. Palantir Technologies sponsors H-1B visas and provides full immigration support.",
        job_apply_link="https://palantir.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-014",
        job_title="AI Engineer",
        employer_name="OpenAI",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="Build AI systems that benefit humanity. Python, ML, PyTorch, large language models. OpenAI sponsors H-1B visas and supports OPT candidates.",
        job_apply_link="https://openai.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
    RawJob(
        job_id="stub-015",
        job_title="Backend Software Engineer",
        employer_name="Lyft",
        job_city="San Francisco", job_state="CA", job_country="US",
        job_description="Scale ride-sharing at millions of trips per day. Python, Go, Kafka, distributed systems. Lyft provides H-1B sponsorship and immigration support for all qualified hires.",
        job_apply_link="https://lyft.com/careers",
        job_employment_type="FULLTIME",
        job_is_remote=False,
    ),
]


def _extract_tags(query: str) -> str:
    """Pull the first recognizable tech skill from the query for Jobicy tag filter."""
    skills = [
        "python", "javascript", "typescript", "java", "go", "rust", "c++",
        "react", "node", "fastapi", "django", "machine-learning", "data",
        "devops", "kubernetes", "aws", "backend", "frontend", "fullstack",
    ]
    lower = query.lower()
    for skill in skills:
        if skill in lower:
            return skill
    return "software"


async def fetch_jobs(query: str, location: str = "United States") -> tuple[list[RawJob], bool]:
    """Returns (jobs, used_stub).
    Primary: Jobicy API (free, no auth, real remote jobs).
    Fallback: stub data.
    """
    try:
        tag = _extract_tags(query)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://jobicy.com/api/v2/remote-jobs",
                params={"tag": tag, "count": "20"},
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            payload = resp.json()
            jobs_data = payload.get("jobs", [])
            if not jobs_data:
                return STUB_JOBS, True
            # Deduplicate by title+company
            seen: set[str] = set()
            unique: list[RawJob] = []
            for i, j in enumerate(jobs_data):
                key = f"{j.get('jobTitle','').lower()}|{j.get('companyName','').lower()}"
                if key not in seen:
                    seen.add(key)
                    unique.append(_map_jobicy(j, i))
            return unique[:20], False
    except Exception:
        return STUB_JOBS, True
