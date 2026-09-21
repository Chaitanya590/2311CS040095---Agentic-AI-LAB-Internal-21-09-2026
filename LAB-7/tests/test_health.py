"""
Health Endpoint Tests
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8006
    assert "Experiment 07" in data["app"]
    assert data["max_reflection_iterations"] == 3
