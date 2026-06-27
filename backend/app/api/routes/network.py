from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.network import NetworkAnalysisRequest, NetworkAnalysisResponse
from app.agents.network_agent import analyze_network
from app.services.linkedin_parser import parse_linkedin_csv
import json

router = APIRouter(prefix="/api/network", tags=["network"])


@router.post("/analyze", response_model=NetworkAnalysisResponse)
async def analyze_connections(
    file: UploadFile = File(...),
    request_json: str = Form(...),
):
    """
    Upload LinkedIn Connections.csv + candidate context.
    Returns ranked outreach messages for relevant connections.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")

    connections = parse_linkedin_csv(content)
    if not connections:
        raise HTTPException(
            status_code=400,
            detail="Could not parse CSV. Make sure this is a LinkedIn Connections export.",
        )

    try:
        req_data = json.loads(request_json)
        request = NetworkAnalysisRequest(
            connections=connections,
            **req_data,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid request data: {e}")

    try:
        result = await analyze_network(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network analysis failed: {str(e)}")
