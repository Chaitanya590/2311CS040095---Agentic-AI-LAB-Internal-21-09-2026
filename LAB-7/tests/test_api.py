"""
FastAPI Integration Tests
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_topics_endpoint():
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 3
    assert "title" in topics[0]

def test_api_research_endpoint():
    response = client.post("/api/research/run", json={
        "topic": "Post-Quantum Cryptography & Enterprise Migration",
        "max_reflection_loops": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["final_quality_score"] >= 80
    assert len(data["research_plan"]) == 3
    assert "Executive Summary" in data["final_dossier_markdown"]
