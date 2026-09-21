"""
Reflection Agent Unit Tests
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from app.services.planner import ResearchPlannerAgent
from app.services.researcher import TopicResearcherAgent
from app.services.reflection import ReflectionAgent

def test_reflection_evaluation():
    planner = ResearchPlannerAgent()
    researcher = TopicResearcherAgent()
    reflector = ReflectionAgent()

    plan = planner.create_research_plan("Cyber Security AI")
    findings = [researcher.execute_subtopic_research(p, iteration=1) for p in plan]

    critique = reflector.evaluate_research(findings, iteration=1)

    assert critique.iteration == 1
    assert critique.quality_score > 0
    assert len(critique.critique_notes) > 0

def test_reflection_score_growth():
    planner = ResearchPlannerAgent()
    researcher = TopicResearcherAgent()
    reflector = ReflectionAgent()

    plan = planner.create_research_plan("Cyber Security AI")
    findings_iter1 = [researcher.execute_subtopic_research(p, iteration=1) for p in plan]
    findings_iter2 = [researcher.execute_subtopic_research(p, iteration=2) for p in plan]

    critique1 = reflector.evaluate_research(findings_iter1, iteration=1)
    critique2 = reflector.evaluate_research(findings_iter2, iteration=2)

    assert critique2.quality_score > critique1.quality_score
    assert critique2.is_sufficient is True
