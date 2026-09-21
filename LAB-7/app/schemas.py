"""
Pydantic API Request/Response Schemas
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    topic: str = Field(
        default="Autonomous AI Multi-Agent Systems in Cyber Defense",
        description="Core research topic or query to investigate"
    )
    max_reflection_loops: int = Field(
        default=2, ge=1, le=5,
        description="Maximum reflection and refinement iterations (capped at 3 internally)"
    )

class SubtopicPlan(BaseModel):
    subtopic_id: str
    title: str
    key_objectives: List[str]

class ResearchFinding(BaseModel):
    subtopic_id: str
    subtopic_title: str
    synthesized_content: str
    key_findings: List[str]
    confidence_rating: float

class ReflectionCritique(BaseModel):
    iteration: int
    quality_score: int  # 0 to 100
    is_sufficient: bool
    critique_notes: List[str]
    missing_aspects: List[str]
    suggested_improvements: List[str]

class AgentStepTrace(BaseModel):
    step: int
    agent_name: str
    action_type: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str
    duration_ms: float

class ResearchDossierResponse(BaseModel):
    topic: str
    research_plan: List[SubtopicPlan]
    findings: List[ResearchFinding]
    reflection_history: List[ReflectionCritique]
    final_dossier_markdown: str
    final_quality_score: int
    total_iterations_executed: int
    agent_traces: List[AgentStepTrace]
    workflow_duration_ms: float
