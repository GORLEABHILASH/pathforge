from pydantic import BaseModel
from typing import Optional


class Connection(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    company: str
    position: str
    connected_on: Optional[str] = None


class NetworkMatch(BaseModel):
    connection: Connection
    relevance_score: int          # 0-100
    company_is_hiring: bool
    why_relevant: str             # one sentence
    shared_context: str           # what you have in common to open with


class OutreachMessage(BaseModel):
    connection: Connection
    relevance_score: int
    company_is_hiring: bool
    why_relevant: str
    subject: str                  # email subject line
    message: str                  # the full outreach message


class NetworkAnalysisRequest(BaseModel):
    connections: list[Connection]
    candidate_name: str
    candidate_skills: list[str]
    candidate_email: str
    target: str
    goal: str
    visa_status: str
    specific_companies: Optional[list[str]] = None
    matched_job_companies: Optional[list[str]] = None  # from job matching results


class NetworkAnalysisResponse(BaseModel):
    total_connections: int
    matched_connections: int
    outreach_messages: list[OutreachMessage]
