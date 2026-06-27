import re
from app.models.jobs import RawJob

SPONSOR_KEYWORDS = [
    "h-1b", "h1b", "visa sponsor", "visa sponsorship", "will sponsor",
    "immigration support", "work authorization", "work authoriz",
    "authorized to work", "ead", "stem opt", "opt authorization",
    "sponsorship available", "sponsor work", "support visa",
]

NEEDS_SPONSORSHIP = {"F-1 Student", "OPT", "STEM OPT"}

KNOWN_SPONSORS: frozenset[str] = frozenset([
    # Large tech
    "google", "amazon", "microsoft", "meta", "apple", "netflix", "openai",
    "nvidia", "intel", "qualcomm", "amd", "broadcom", "cisco", "oracle",
    "ibm", "salesforce", "adobe", "servicenow", "workday", "snowflake",
    "databricks", "palantir", "splunk", "vmware", "dell", "hp", "sap",
    # High-growth
    "stripe", "airbnb", "uber", "lyft", "doordash", "instacart", "coinbase",
    "robinhood", "figma", "notion", "vercel", "github", "gitlab", "atlassian",
    "slack", "zoom", "twilio", "datadog", "pagerduty", "hashicorp", "mongodb",
    "elastic", "cloudflare", "fastly", "okta", "auth0",
    # Consulting / IT (highest H1B volume by petition count)
    "cognizant", "infosys", "tcs", "tata consultancy", "wipro", "hcl",
    "accenture", "capgemini", "deloitte", "kpmg", "ernst young", "pwc",
    "mckinsey", "boston consulting", "bain",
    # Finance tech
    "jpmorgan", "goldman sachs", "morgan stanley", "blackrock", "citadel",
    "jane street", "two sigma", "hudson river trading", "bloomberg",
    "visa", "mastercard", "paypal", "square", "block",
    # Healthcare tech
    "epic systems", "optum", "unitedhealth", "cvs health", "athenahealth",
    # More tech
    "linkedin", "twitter", "x corp", "pinterest", "snap", "spotify",
    "dropbox", "box", "zendesk", "hubspot", "intercom", "segment",
    "twitch", "roblox", "unity", "electronic arts", "activision",
    "tesla", "rivian", "waymo", "cruise", "aurora",
])

_SUFFIX_PATTERN = re.compile(
    r"\s+(inc\.?|llc\.?|corp\.?|ltd\.?|co\.?|technologies|technology|"
    r"solutions|systems|services|group|holdings|international|global)$",
    re.IGNORECASE,
)


def _normalize_company(name: str) -> str:
    normalized = _SUFFIX_PATTERN.sub("", name.strip()).lower()
    return normalized


def _check_jd_keywords(description: str) -> bool:
    text = description.lower()
    return any(kw in text for kw in SPONSOR_KEYWORDS)


def _check_known_sponsors(employer_name: str) -> bool:
    normalized = _normalize_company(employer_name)
    return normalized in KNOWN_SPONSORS


def _score_visa(job: RawJob) -> tuple[str, str]:
    jd_hit = _check_jd_keywords(job.job_description)
    list_hit = _check_known_sponsors(job.employer_name)

    if jd_hit and list_hit:
        return (
            "confirmed",
            f"JD explicitly mentions sponsorship + {job.employer_name} is a known H-1B sponsor (USCIS data)",
        )
    elif jd_hit:
        return "confirmed", "Job description explicitly mentions visa sponsorship"
    elif list_hit:
        return "likely", f"{job.employer_name} is a historically active H-1B sponsor (USCIS public data)"
    else:
        return "unknown", "No visa sponsorship signals detected in this posting"


def filter_jobs(
    jobs: list[RawJob], visa_status: str
) -> list[tuple[RawJob, str, str]]:
    """Returns list of (job, visa_confidence, visa_signal)."""
    results = []
    for job in jobs:
        confidence, signal = _score_visa(job)
        if visa_status in NEEDS_SPONSORSHIP:
            if confidence in ("confirmed", "likely"):
                results.append((job, confidence, signal))
        else:
            results.append((job, "not_required", "Your visa status does not require sponsorship filtering"))
    return results
