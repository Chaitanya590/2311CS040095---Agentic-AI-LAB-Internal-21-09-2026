"""
Synthetic Research Knowledge Dataset Generator
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
Generates structured sample research topics and reference data.
"""

import json
import os

SAMPLE_RESEARCH_TOPICS = [
    {
        "topic_id": "TOPIC-01",
        "title": "Autonomous AI Multi-Agent Systems in Cyber Defense",
        "domain": "Cybersecurity & Agentic AI",
        "description": "Comprehensive analysis of multi-agent architectures, SOC triage automation, threat hunting loops, and safety safeguards.",
        "default_subtopics": [
            "Architectural Patterns of Multi-Agent Systems",
            "Real-Time Incident Triage & Response Automation",
            "Ethical Safeguards & Human-in-the-Loop Governance"
        ]
    },
    {
        "topic_id": "TOPIC-02",
        "title": "Post-Quantum Cryptography & Enterprise Migration",
        "domain": "Cryptography & Quantum Computing",
        "description": "Deep research report examining lattice-based cryptography, NIST PQC standardization, and corporate infrastructure migration roadmaps.",
        "default_subtopics": [
            "NIST Post-Quantum Cryptographic Standards Overview",
            "Harvest-Now-Decrypt-Later Threat Vector Analysis",
            "Enterprise Hybrid Migration Implementation Plan"
        ]
    },
    {
        "topic_id": "TOPIC-03",
        "title": "Hybrid Vector-Lexical RAG Architectures for Medical QA",
        "domain": "Biomedical AI & RAG",
        "description": "Evaluation of hybrid BM25 + Dense vector retrieval pipelines for clinical trial data extraction and medical query answering.",
        "default_subtopics": [
            "Dense Vector vs Lexical Keyword Retrieval Benchmarks",
            "Clinical Context Chunking & Re-ranking Strategies",
            "Hallucination Mitigation in High-Stakes Domain QA"
        ]
    }
]

def generate_research_data(output_path: str = None):
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "sample_topics.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_RESEARCH_TOPICS, f, indent=2)

    print(f"[OK] Generated {len(SAMPLE_RESEARCH_TOPICS)} sample research topics -> {output_path}")

if __name__ == "__main__":
    generate_research_data()
