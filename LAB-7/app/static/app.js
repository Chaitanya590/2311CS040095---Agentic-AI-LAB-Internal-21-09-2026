/**
 * Interactive Client Controller
 * Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
 */

document.addEventListener('DOMContentLoaded', () => {
    const researchForm = document.getElementById('research-form');
    const researchTopicInput = document.getElementById('research-topic');
    const maxLoopsInput = document.getElementById('max-loops');
    const runResearchBtn = document.getElementById('run-research-btn');
    const sampleTopicsContainer = document.getElementById('sample-topics-container');

    const welcomeCard = document.getElementById('welcome-card');
    const resultsArea = document.getElementById('results-area');
    const durationBadge = document.getElementById('duration-badge');

    const qualityScoreVal = document.getElementById('quality-score-val');
    const subtopicsCountVal = document.getElementById('subtopics-count-val');
    const iterationsCountVal = document.getElementById('iterations-count-val');

    const reflectionTimeline = document.getElementById('reflection-timeline');
    const dossierMarkdownContent = document.getElementById('dossier-markdown-content');

    fetchSampleTopics();

    researchForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const topic = researchTopicInput.value.trim();
        const maxLoops = parseInt(maxLoopsInput.value, 10) || 2;

        if (!topic) {
            alert('Please enter a research topic.');
            return;
        }

        runResearchBtn.disabled = true;
        runResearchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Executing Research & Reflection Loops...';
        welcomeCard.style.display = 'none';
        resultsArea.style.display = 'block';

        try {
            const res = await fetch('/api/research/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic, max_reflection_loops: maxLoops })
            });

            if (!res.ok) {
                throw new Error(`HTTP Error: ${res.status}`);
            }

            const data = await res.json();
            renderResearchResults(data);
        } catch (err) {
            alert(`Deep Research Error: ${err.message}`);
        } finally {
            runResearchBtn.disabled = false;
            runResearchBtn.innerHTML = '<span>Launch Deep Research Workflow</span> <i class="fa-solid fa-rocket"></i>';
        }
    });

    async function fetchSampleTopics() {
        try {
            const res = await fetch('/api/topics');
            if (res.ok) {
                const topics = await res.json();
                let html = '';
                topics.forEach(t => {
                    html += `
                        <button type="button" class="sample-btn" data-title="${escapeHtml(t.title)}">
                            <i class="fa-solid fa-lightbulb"></i> ${t.title}
                        </button>
                    `;
                });
                sampleTopicsContainer.innerHTML = html;

                const sampleBtns = sampleTopicsContainer.querySelectorAll('.sample-btn');
                sampleBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        researchTopicInput.value = btn.getAttribute('data-title');
                        researchTopicInput.focus();
                    });
                });
            }
        } catch (e) {
            console.warn('Sample topics fetch error:', e);
        }
    }

    function escapeHtml(str) {
        return str.replace(/"/g, '&quot;');
    }

    function renderResearchResults(data) {
        durationBadge.style.display = 'inline-block';
        durationBadge.textContent = `${data.workflow_duration_ms} ms`;

        qualityScoreVal.textContent = `${data.final_quality_score}/100`;
        subtopicsCountVal.textContent = data.research_plan ? data.research_plan.length : 0;
        iterationsCountVal.textContent = data.total_iterations_executed || 0;

        renderAgentTraces(data.agent_traces || []);
        dossierMarkdownContent.textContent = data.final_dossier_markdown || 'No dossier generated.';
    }

    function renderAgentTraces(traces) {
        if (!traces || traces.length === 0) {
            reflectionTimeline.innerHTML = '<p class="subtitle">No agent execution traces recorded.</p>';
            return;
        }

        let html = '';
        traces.forEach(t => {
            html += `
                <div class="timeline-item">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                        <span style="font-weight:700; color:var(--secondary); font-size:0.85rem;"><i class="fa-solid fa-robot"></i> ${t.agent_name}</span>
                        <span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">${t.duration_ms} ms</span>
                    </div>
                    <div style="font-size:0.85rem;"><strong>Action:</strong> ${t.description}</div>
                    <div style="font-size:0.8rem; background:rgba(0,0,0,0.3); padding:0.4rem 0.6rem; border-radius:4px; margin-top:0.4rem; font-family:var(--font-mono); color:var(--text-muted);">
                        ${JSON.stringify(t.outputs)}
                    </div>
                </div>
            `;
        });
        reflectionTimeline.innerHTML = html;
    }
});
