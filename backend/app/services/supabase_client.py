import os
from typing import Optional
from supabase import create_client, Client

_client: Optional[Client] = None


def get_client() -> Optional[Client]:
    global _client
    if _client:
        return _client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    _client = create_client(url, key)
    return _client


def is_available() -> bool:
    return get_client() is not None
