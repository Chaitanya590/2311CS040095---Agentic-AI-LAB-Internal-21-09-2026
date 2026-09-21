"""
FastAPI Server Entry Point & Router
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
Port: 8006
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, List
import json
import os

from app.config import settings
from app.schemas import ResearchRequest, ResearchDossierResponse
from app.services.supervisor import DeepResearchSupervisor

app = FastAPI(
    title="Experiment 07 — Deep Research Agent Workflow",
    description="Multi-agent planning, research synthesis, and reflection workflow.",
    version="1.0.0"
)

# Mount static UI assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

supervisor = DeepResearchSupervisor()

@app.get("/")
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "app": "Experiment 07 — Deep Research Agent Workflow",
        "course": "Applied Agentic AI Laboratory (MR23-1CS0436)",
        "status": "online",
        "port": settings.PORT
    })

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Experiment 07 — Deep Research Agent Workflow",
        "course": "Applied Agentic AI Laboratory (MR23-1CS0436)",
        "port": settings.PORT,
        "llm_provider": settings.LLM_PROVIDER,
        "max_reflection_iterations": settings.MAX_REFLECTION_ITERATIONS
    }

@app.get("/api/topics")
async def get_sample_topics():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    t_path = os.path.join(base_dir, settings.SAMPLE_TOPICS_FILE_PATH)
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/research/run", response_model=ResearchDossierResponse)
async def run_deep_research(req: ResearchRequest):
    try:
        response = supervisor.run_deep_research(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep Research Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
