"""
Planner Agent Unit Tests
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from app.services.planner import ResearchPlannerAgent

def test_planner_subtopic_decomposition():
    planner = ResearchPlannerAgent()
    subtopics = planner.create_research_plan("Autonomous AI Multi-Agent Systems in Cyber Defense")

    assert len(subtopics) == 3
    ids = [s.subtopic_id for s in subtopics]
    assert "SUB-01" in ids
    assert len(subtopics[0].key_objectives) >= 2

def test_planner_quantum_topic():
    planner = ResearchPlannerAgent()
    subtopics = planner.create_research_plan("Post-Quantum Cryptography Enterprise Migration")

    assert len(subtopics) == 3
    assert "PQC" in subtopics[0].title or "Post-Quantum" in subtopics[0].title
