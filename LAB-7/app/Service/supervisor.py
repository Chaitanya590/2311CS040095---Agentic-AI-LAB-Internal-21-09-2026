"""
Research Supervisor Orchestrator Agent
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
Coordinates Planner, Researcher, Reflection, and Synthesizer agents in a bounded reflection loop.
"""

import time
from typing import List, Dict, Any
from app.config import settings
from app.schemas import (
    ResearchRequest, ResearchDossierResponse, SubtopicPlan, 
    ResearchFinding, ReflectionCritique, AgentStepTrace
)
from app.services.planner import ResearchPlannerAgent
from app.services.researcher import TopicResearcherAgent
from app.services.reflection import ReflectionAgent
from app.services.synthesizer import ReportSynthesizerAgent

class DeepResearchSupervisor:
    def __init__(self):
        self.planner = ResearchPlannerAgent()
        self.researcher = TopicResearcherAgent()
        self.reflection_agent = ReflectionAgent()
        self.synthesizer = ReportSynthesizerAgent()

    def run_deep_research(self, req: ResearchRequest) -> ResearchDossierResponse:
        start_time = time.time()
        traces: List[AgentStepTrace] = []
        step_counter = 1

        # Enforce strict reflection iteration cap (Max 3)
        max_loops = min(req.max_reflection_loops, settings.MAX_REFLECTION_ITERATIONS)

        # 1. Research Planning Step
        t0 = time.time()
        plan = self.planner.create_research_plan(req.topic)
        t1 = time.time()

        traces.append(AgentStepTrace(
            step=step_counter,
            agent_name="Supervisor -> Research Planner Agent",
            action_type="CREATE_RESEARCH_PLAN",
            description=f"Decomposed topic '{req.topic}' into {len(plan)} target subtopics.",
            inputs={"topic": req.topic},
            outputs={"subtopics_count": len(plan), "subtopic_ids": [p.subtopic_id for p in plan]},
            status="SUCCESS",
            duration_ms=round((t1 - t0) * 1000, 2)
        ))
        step_counter += 1

        findings: List[ResearchFinding] = []
        reflection_history: List[ReflectionCritique] = []

        # 2. Bounded Research & Reflection Loop
        for iteration in range(1, max_loops + 1):
            # Research Step
            t0 = time.time()
            current_findings = []
            for p in plan:
                f_res = self.researcher.execute_subtopic_research(p, iteration)
                current_findings.append(f_res)
            t1 = time.time()

            findings = current_findings

            traces.append(AgentStepTrace(
                step=step_counter,
                agent_name="Supervisor -> Topic Researcher Agent",
                action_type=f"EXECUTE_RESEARCH_ITERATION_{iteration}",
                description=f"Gathered technical research findings across {len(plan)} subtopics (Iteration {iteration}).",
                inputs={"iteration": iteration, "subtopics_count": len(plan)},
                outputs={"findings_count": len(findings)},
                status="SUCCESS",
                duration_ms=round((t1 - t0) * 1000, 2)
            ))
            step_counter += 1

            # Reflection Step
            t0 = time.time()
            critique = self.reflection_agent.evaluate_research(findings, iteration)
            reflection_history.append(critique)
            t1 = time.time()

            traces.append(AgentStepTrace(
                step=step_counter,
                agent_name="Supervisor -> Reflection Agent",
                action_type=f"EVALUATE_REFLECTION_ITERATION_{iteration}",
                description=f"Critiqued research quality at Iteration {iteration}. Score: {critique.quality_score}/100. Sufficient: {critique.is_sufficient}.",
                inputs={"iteration": iteration},
                outputs={"quality_score": critique.quality_score, "is_sufficient": critique.is_sufficient},
                status="SUCCESS",
                duration_ms=round((t1 - t0) * 1000, 2)
            ))
            step_counter += 1

            if critique.is_sufficient:
                break

        # 3. Final Report Synthesis Step
        t0 = time.time()
        dossier_md = self.synthesizer.synthesize_dossier(req.topic, plan, findings, reflection_history)
        t1 = time.time()

        traces.append(AgentStepTrace(
            step=step_counter,
            agent_name="Supervisor -> Report Synthesizer Agent",
            action_type="SYNTHESIZE_DOSSIER",
            description="Compiled polished markdown research dossier with executive summary and technical recommendations.",
            inputs={"topic": req.topic, "iterations": len(reflection_history)},
            outputs={"markdown_length_chars": len(dossier_md)},
            status="SUCCESS",
            duration_ms=round((t1 - t0) * 1000, 2)
        ))

        total_duration = round((time.time() - start_time) * 1000, 2)
        final_score = reflection_history[-1].quality_score if reflection_history else 85

        return ResearchDossierResponse(
            topic=req.topic,
            research_plan=plan,
            findings=findings,
            reflection_history=reflection_history,
            final_dossier_markdown=dossier_md,
            final_quality_score=final_score,
            total_iterations_executed=len(reflection_history),
            agent_traces=traces,
            workflow_duration_ms=total_duration
        )
