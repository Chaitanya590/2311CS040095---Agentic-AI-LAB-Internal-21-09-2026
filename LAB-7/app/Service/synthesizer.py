"""
Report Synthesizer Agent
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
Compiles subtopic findings and reflection feedback into a structured technical markdown dossier.
"""

from typing import List, Dict, Any
from app.schemas import SubtopicPlan, ResearchFinding, ReflectionCritique

class ReportSynthesizerAgent:
    def __init__(self):
        self.agent_name = "Report Synthesizer Agent"

    def synthesize_dossier(
        self,
        topic: str,
        plan: List[SubtopicPlan],
        findings: List[ResearchFinding],
        reflections: List[ReflectionCritique]
    ) -> str:
        last_reflection = reflections[-1] if reflections else None
        quality_score = last_reflection.quality_score if last_reflection else 85

        md_parts = []
        md_parts.append(f"# Deep Research Dossier: {topic}\n")
        md_parts.append(f"**Course Code:** MR23-1CS0436 — Applied Agentic AI Laboratory  ")
        md_parts.append(f"**Module:** Experiment 07 — Deep Research Agent Workflow  ")
        md_parts.append(f"**Quality Rating:** {quality_score}/100 · **Iterations Executed:** {len(reflections)}  \n")

        md_parts.append("## Executive Summary")
        md_parts.append(
            f"This autonomous deep research report evaluates **{topic}** through iterative planning, "
            f"subtopic decomposition, and multi-round quality reflection loops. The investigation verified "
            f"core architectural patterns and synthesized actionable technical insights across {len(plan)} subtopics.\n"
        )

        md_parts.append("## Structured Research Plan")
        for p in plan:
            md_parts.append(f"- **{p.subtopic_id}: {p.title}**")
            for obj in p.key_objectives:
                md_parts.append(f"  - *Objective:* {obj}")
        md_parts.append("")

        md_parts.append("## Detailed Subtopic Research Findings")
        for f in findings:
            md_parts.append(f.synthesized_content)
            md_parts.append("\n**Key Findings Summary:**")
            for kf in f.key_findings:
                md_parts.append(f"- {kf}")
            md_parts.append("")

        md_parts.append("## Reflection & Quality Critique Log")
        for r in reflections:
            md_parts.append(f"### Iteration {r.iteration} (Quality Score: {r.quality_score}/100)")
            for note in r.critique_notes:
                md_parts.append(f"- {note}")
            if r.suggested_improvements:
                md_parts.append(f"- **Improvements:** {', '.join(r.suggested_improvements)}")
            md_parts.append("")

        md_parts.append("## Strategic Technical Recommendations")
        md_parts.append(
            "1. **Architectural Standard:** Implement explicit state contracts between supervisor and worker sub-agents.\n"
            "2. **Continuous Reflection:** Enforce bounded reflection loops (max 3) to prevent infinite refinement cycles.\n"
            "3. **Verification Testing:** Validate research outputs against automated test suites prior to deployment."
        )

        return "\n".join(md_parts)
