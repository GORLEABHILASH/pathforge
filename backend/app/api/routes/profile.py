from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.profile import ProfileCreateRequest, ProfileResponse, OnboardingInput
from app.agents.profile_agent import extract_profile
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


@router.post("/assess", response_model=ProfileResponse)
async def assess_profile(request: ProfileCreateRequest):
    try:
        profile = await extract_profile(request.onboarding)
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
