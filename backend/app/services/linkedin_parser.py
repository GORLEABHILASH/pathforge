import csv
import io
from typing import Optional
from app.models.network import Connection

# LinkedIn CSV columns (may vary slightly by export date)
_COLUMN_ALIASES = {
    "first_name": ["first name", "firstname"],
    "last_name": ["last name", "lastname"],
    "url": ["url", "linkedin url", "profile url"],
    "email": ["email address", "email"],
    "company": ["company", "current company"],
    "position": ["position", "title", "job title"],
    "connected_on": ["connected on", "connection date"],
}


def _find_col(headers: list[str], aliases: list[str]) -> Optional[str]:
    lower = [h.lower().strip() for h in headers]
    for alias in aliases:
        if alias in lower:
            return headers[lower.index(alias)]
    return None


def parse_linkedin_csv(content: bytes) -> list[Connection]:
    """
    Parse LinkedIn Connections.csv export.
    LinkedIn adds a few header lines before the actual CSV — skip them.
    """
    text = content.decode("utf-8", errors="replace")
    lines = text.splitlines()

    # Find the line that contains "First Name" — that's the real header
    header_idx = None
    for i, line in enumerate(lines):
        if "first name" in line.lower() or "firstname" in line.lower():
            header_idx = i
            break

    if header_idx is None:
        return []

    csv_text = "\n".join(lines[header_idx:])
    reader = csv.DictReader(io.StringIO(csv_text))
    headers = reader.fieldnames or []

    col = {
        key: _find_col(list(headers), aliases)
        for key, aliases in _COLUMN_ALIASES.items()
    }

    connections: list[Connection] = []
    for row in reader:
        company = (row.get(col["company"]) or "").strip()
        position = (row.get(col["position"]) or "").strip()
        first = (row.get(col["first_name"]) or "").strip()
        last = (row.get(col["last_name"]) or "").strip()

        if not first or not company:
            continue

        connections.append(
            Connection(
                first_name=first,
                last_name=last,
                full_name=f"{first} {last}".strip(),
                linkedin_url=row.get(col["url"], "").strip() or None,
                email=row.get(col["email"], "").strip() or None,
                company=company,
                position=position,
                connected_on=row.get(col["connected_on"], "").strip() or None,
            )
        )

    return connections
