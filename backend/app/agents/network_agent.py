import anthropic
from app.models.network import (
    Connection,
    NetworkAnalysisRequest,
    NetworkAnalysisResponse,
    OutreachMessage,
)
from app.services.visa_filter import KNOWN_SPONSORS

client = anthropic.Anthropic()

OUTREACH_TOOL = {
    "name": "generate_outreach",
    "description": (
        "For each relevant connection, generate a specific, non-generic outreach message. "
        "Messages must be personal, direct, and ask for exactly one thing. "
        "No 'hope this finds you well'. No 'pick your brain'. No generic networking fluff."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "outreach": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string"},
                        "company": {"type": "string"},
                        "relevance_score": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "How valuable this connection is for the job search. 90+ = works at target company in relevant role. 70+ = works at target company. 50+ = adjacent company or relevant industry.",
                        },
                        "company_is_hiring": {
                            "type": "boolean",
                            "description": "True if this company is likely hiring based on the candidate's job matches",
                        },
                        "why_relevant": {
                            "type": "string",
                            "description": "One sentence: why this specific connection matters for THIS candidate's job search",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line — specific, not 'Quick question' or 'Reaching out'",
                        },
                        "message": {
                            "type": "string",
                            "description": (
                                "The outreach message. Rules: "
                                "(1) Open with shared context — how you know them or what you have in common. "
                                "(2) One sentence on what you're looking for — specific role and company. "
                                "(3) One clear ask — intro to someone on X team, referral, or 15-min call. "
                                "(4) Under 120 words. "
                                "(5) NO: 'hope this finds you well', 'pick your brain', 'touch base', 'circle back'. "
                                "(6) Sound human, not AI."
                            ),
                        },
                    },
                    "required": [
                        "full_name", "company", "relevance_score",
                        "company_is_hiring", "why_relevant", "subject", "message",
                    ],
                },
            }
        },
        "required": ["outreach"],
    },
}

# High-value company tiers for relevance scoring
FAANG = {"google", "meta", "apple", "amazon", "microsoft", "netflix", "openai", "nvidia"}
HIGH_GROWTH = {"stripe", "airbnb", "figma", "notion", "linear", "vercel", "databricks", "snowflake"}


def _is_relevant_company(company: str, request: NetworkAnalysisRequest) -> bool:
    """Quick pre-filter before sending to Claude."""
    lower = company.lower()
    # Check stated target companies
    if request.specific_companies:
        for t in request.specific_companies:
            if t.lower() in lower or lower in t.lower():
                return True
    # Check matched job companies
    if request.matched_job_companies:
        for c in request.matched_job_companies:
            if c.lower() in lower or lower in c.lower():
                return True
    # Check known sponsor list (200+ companies)
    for sponsor in KNOWN_SPONSORS:
        if sponsor in lower:
            return True
    return False


def _pre_filter(
    connections: list[Connection], request: NetworkAnalysisRequest
) -> list[Connection]:
    """
    Keep connections at relevant companies.
    Cap at 30 to keep the Claude prompt manageable.
    Prioritize: FAANG > high growth > known sponsors > others.
    """
    def priority(c: Connection) -> int:
        lower = c.company.lower()
        if any(f in lower for f in FAANG):
            return 3
        if any(h in lower for h in HIGH_GROWTH):
            return 2
        if _is_relevant_company(c.company, request):
            return 1
        return 0

    relevant = [c for c in connections if _is_relevant_company(c.company, request)]
    relevant.sort(key=priority, reverse=True)
    return relevant[:30]


async def analyze_network(request: NetworkAnalysisRequest) -> NetworkAnalysisResponse:
    filtered = _pre_filter(request.connections, request)

    if not filtered:
        return NetworkAnalysisResponse(
            total_connections=len(request.connections),
            matched_connections=0,
            outreach_messages=[],
        )

    connections_str = "\n".join(
        f"- {c.full_name} | {c.position} at {c.company}"
        + (f" | connected {c.connected_on}" if c.connected_on else "")
        for c in filtered
    )

    hiring_companies = ", ".join(request.matched_job_companies or [])

    prompt = f"""You are PathForge's warm introduction agent. Generate personalized outreach messages for these connections.

CANDIDATE:
Name: {request.candidate_name}
Email: {request.candidate_email}
Skills: {', '.join(request.candidate_skills[:10])}
Target: {request.target}
Goal: {request.goal}
Visa: {request.visa_status}

COMPANIES CURRENTLY HIRING (from job matches): {hiring_companies or 'unknown'}

CONNECTIONS TO ANALYZE:
{connections_str}

For each connection:
1. Score relevance 0-100 (higher = works at a company the candidate should be at)
2. Mark company_is_hiring=true if the company appears in the hiring list above
3. Write a specific outreach message — personal, under 120 words, one clear ask
4. Subject line must be specific (e.g. "Engineering roles at Stripe — connection from [University]")

CRITICAL: Messages must NOT sound like AI wrote them. No templates. Each message must reference the specific person's company and role.

Use the generate_outreach tool."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=[OUTREACH_TOOL],
        tool_choice={"type": "tool", "name": "generate_outreach"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    outreach_data = tool_use.input["outreach"]

    # Map Claude output back to Connection objects
    conn_by_name = {c.full_name.lower(): c for c in filtered}
    messages: list[OutreachMessage] = []

    for item in outreach_data:
        name_key = item["full_name"].lower()
        connection = conn_by_name.get(name_key)
        if not connection:
            # fuzzy match on first word
            first = item["full_name"].split()[0].lower()
            connection = next(
                (c for k, c in conn_by_name.items() if k.startswith(first)),
                None,
            )
        if not connection:
            connection = Connection(
                first_name=item["full_name"].split()[0],
                last_name=" ".join(item["full_name"].split()[1:]),
                full_name=item["full_name"],
                company=item["company"],
                position="",
            )

        messages.append(
            OutreachMessage(
                connection=connection,
                relevance_score=item["relevance_score"],
                company_is_hiring=item["company_is_hiring"],
                why_relevant=item["why_relevant"],
                subject=item["subject"],
                message=item["message"],
            )
        )

    messages.sort(key=lambda x: x.relevance_score, reverse=True)

    return NetworkAnalysisResponse(
        total_connections=len(request.connections),
        matched_connections=len(messages),
        outreach_messages=messages[:15],  # top 15
    )
