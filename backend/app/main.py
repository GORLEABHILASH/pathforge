from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import profile, jobs, skills, network

app = FastAPI(
    title="PathForge API",
    description="Career intelligence platform for international students and engineers",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(skills.router)
app.include_router(network.router)


@app.get("/")
async def root():
    return {"message": "PathForge API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
