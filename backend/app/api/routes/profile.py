from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.profile import ProfileCreateRequest, ProfileResponse, OnboardingInput
from app.agents.profile_agent import extract_profile
from app.services.supabase_client import get_client, is_available
import PyPDF2
import io

router = APIRouter(prefix="/api/profile", tags=["profile"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


@router.post("/extract-from-pdf")
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    text = extract_text_from_pdf(content)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    return {"resume_text": text}


def _persist_profile(email: str, profile, onboarding) -> None:
    """Save user + profile to Supabase. Silently skips if DB not configured."""
    if not is_available():
        return
    try:
        db = get_client()
        # Upsert user (has unique constraint on email)
        db.table("users").upsert({"email": email}, on_conflict="email").execute()
        # Insert or update profile (no unique constraint — use select + insert/update)
        payload = {
            "user_email": email,
            "profile_json": profile.model_dump(),
            "onboarding_json": onboarding.model_dump(),
            "employability_score": profile.employability_score,
        }
        existing = db.table("profiles").select("id").eq("user_email", email).execute()
        if existing.data:
            db.table("profiles").update(payload).eq("user_email", email).execute()
        else:
            db.table("profiles").insert(payload).execute()
    except Exception:
        pass  # Never block the response due to a DB write failure


@router.post("/assess", response_model=ProfileResponse)
async def assess_profile(request: ProfileCreateRequest):
    try:
        profile = await extract_profile(request.onboarding)
        _persist_profile(request.email, profile, request.onboarding)
        return ProfileResponse(
            profile=profile,
            onboarding=request.onboarding,
            email=request.email,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile assessment failed: {str(e)}")


@router.post("/assess-text", response_model=ProfileResponse)
async def assess_from_text(request: ProfileCreateRequest):
    """Assess profile directly from resume text — no PDF needed."""
    try:
        profile = await extract_profile(request.onboarding)
        return ProfileResponse(
            profile=profile,
            onboarding=request.onboarding,
            email=request.email,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile assessment failed: {str(e)}")
