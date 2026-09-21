"""
Supervisor Orchestrator Unit Tests
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from app.schemas import ResearchRequest
from app.services.supervisor import DeepResearchSupervisor

def test_supervisor_deep_research_workflow():
    supervisor = DeepResearchSupervisor()
    req = ResearchRequest(
        topic="Autonomous AI Multi-Agent Systems in Cyber Defense",
        max_reflection_loops=2
    )

    res = supervisor.run_deep_research(req)

    assert len(res.research_plan) == 3
    assert len(res.findings) == 3
    assert res.total_iterations_executed >= 1
    assert res.final_quality_score >= 80
    assert "Deep Research Dossier" in res.final_dossier_markdown
    assert len(res.agent_traces) >= 4

def test_supervisor_max_iteration_cap():
    supervisor = DeepResearchSupervisor()
    req = ResearchRequest(
        topic="General Topic",
        max_reflection_loops=5  # Capped at 3 internally by settings.MAX_REFLECTION_ITERATIONS
    )

    res = supervisor.run_deep_research(req)

    assert res.total_iterations_executed <= 3
