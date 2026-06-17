import sys

js_code = """
// --- Agent Generation from Prompt Logic ---
const createFromPromptBtn = document.getElementById('createFromPromptBtn');
const agentPromptModal = document.getElementById('agentPromptModal');
const closeAgentPromptModalBtn = document.getElementById('closeAgentPromptModalBtn');
const agentPromptForm = document.getElementById('agentPromptForm');
const generateAgentBtn = document.getElementById('generateAgentBtn');
const agentGenLoading = document.getElementById('agentGenLoading');

if (createFromPromptBtn) {
    createFromPromptBtn.addEventListener('click', () => {
        if(agentPromptModal) agentPromptModal.classList.add('active');
        const input = document.getElementById('agentIntentInput');
        if (input) input.value = '';
    });
}
if (closeAgentPromptModalBtn) {
    closeAgentPromptModalBtn.addEventListener('click', () => {
        if(agentPromptModal) agentPromptModal.classList.remove('active');
    });
}

if (agentPromptForm) {
    agentPromptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const intent = document.getElementById('agentIntentInput').value.trim();
        if (!intent) return;
        
        generateAgentBtn.style.display = 'none';
        agentGenLoading.style.display = 'block';
        
        try {
            const res = await authFetch(`/api/agents/generate_from_prompt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: parseInt(projectId), intent: intent })
            });
            
            const data = await res.json();
            
            if (res.ok && data.status === 'success') {
                if(agentPromptModal) agentPromptModal.classList.remove('active');
                await loadAgentsView();
                openAgentConfig(data.agent);
            } else {
                alert('Failed to generate agent: ' + (data.detail || 'Unknown error'));
            }
        } catch (err) {
            console.error('Error generating agent:', err);
            alert('Error generating agent. Check console for details.');
        } finally {
            generateAgentBtn.style.display = 'block';
            agentGenLoading.style.display = 'none';
        }
    });
}
"""

with open('frontend/project.js', 'a', encoding='utf-8') as f:
    f.write("\n" + js_code)
print("project.js patched for agent generation.")
