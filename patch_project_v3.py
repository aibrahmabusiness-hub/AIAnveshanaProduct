import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. State Variables
content = re.sub(
    r"const agentId = parseInt\(pathParts\[pathParts\.length - 1\]\);\s*let agentData = null;",
    "const projectId = parseInt(pathParts[pathParts.length - 1]);\nlet projectData = null;\nlet activeAgentId = null;\nlet activeAgentData = null;",
    content
)

# 2. init() function
init_search = r"async function init\(\) \{[\s\S]*?loadWorkflowsView\(\);\s*\}"
init_replace = """async function init() {
    // Load project info
    const res = await authFetch(`/api/projects/${projectId}`);
    const data = await res.json();
    projectData = data.project;
    document.getElementById('sidebarTitle').textContent = projectData.name;
    document.title = `${projectData.name} - Workspace`;

    // Load agents grid
    await loadProjectAgentsList();

    // Load other views only when clicked, except chat history
    loadChatThreads();
}"""
content = re.sub(init_search, init_replace, content)

# 3. Sidebar Navigation click listener
nav_search = r"document\.querySelectorAll\('\.ws-nav-item\[data-view\]'\)\.forEach\(item => \{[\s\S]*?\}\);\s*\}\);"
nav_replace = """document.querySelectorAll('.ws-nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.ws-nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        const viewId = item.dataset.view;
        document.querySelectorAll('.ws-view').forEach(v => v.classList.remove('active'));
        const targetView = document.getElementById(`view-${viewId}`);
        if(targetView) targetView.classList.add('active');

        // Show/hide history panel based on view
        const historyPanel = document.getElementById('historyPanel');
        if (historyPanel) historyPanel.style.display = viewId === 'chat' ? '' : 'none';

        // Load specific data based on view
        if (viewId === 'tools') loadToolsView();
        else if (viewId === 'knowledge') loadKnowledgeBase();
        else if (viewId === 'workflows') loadWorkflowsView();
        else if (viewId === 'runs') loadWorkflowRuns();
        else if (viewId === 'settings') loadSettingsView();
        else if (viewId === 'chat') loadChatThreads();
        
        // Agent settings logic
        document.getElementById('saveAgentBtn').style.display = viewId === 'agents' ? 'block' : 'none';
        
        if (viewId === 'agents' && activeAgentId) {
             document.getElementById('agents-list-screen').style.display = 'none';
             document.getElementById('agent-config-screen').style.display = 'flex';
        } else if (viewId === 'agents') {
             document.getElementById('agent-config-screen').style.display = 'none';
             document.getElementById('agents-list-screen').style.display = 'block';
        }
    });
});"""
content = re.sub(nav_search, nav_replace, content)

# 4. loadProjectAgentsList implementation
agents_list_func = """
async function loadProjectAgentsList() {
    try {
        const res = await authFetch(`/api/projects/${projectId}/agents`);
        if (!res.ok) throw new Error('Failed to fetch agents');
        const data = await res.json();
        
        const grid = document.getElementById('projectAgentsGrid');
        if (!grid) return;

        // Keep the first two fixed cards, remove dynamically added ones
        const cards = Array.from(grid.children);
        cards.slice(2).forEach(c => c.remove());
        
        const badge = document.getElementById('connectedToolsBadge');
        if(badge) badge.textContent = `${data.agents.length} agent${data.agents.length !== 1 ? 's' : ''}`;

        data.agents.forEach(agent => {
            const card = document.createElement('div');
            card.className = 'agent-hub-card';
            if (agent.id === activeAgentId) {
                card.classList.add('active-card');
            }
            const toolCount = (agent.connected_tools || []).length;
            card.innerHTML = `
                <div class="agent-header">
                    <div class="agent-title">${agent.name}</div>
                    <div class="agent-more">...</div>
                </div>
                <div class="agent-desc">
                    ${agent.description}
                </div>
                <div class="agent-footer">
                    <div class="agent-tools">
                        <div class="tool-box"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg></div>
                        <div class="tool-box count">+${toolCount}</div>
                    </div>
                    <div class="nav-arrow">↗</div>
                </div>
            `;
            card.addEventListener('click', async () => {
                activeAgentId = agent.id;
                const agentRes = await authFetch(`/api/agents/${activeAgentId}`);
                activeAgentData = await agentRes.json();
                
                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agentNameInput').value = activeAgentData.name;
                document.getElementById('agentDescInput').value = activeAgentData.description;
                document.getElementById('personalityPromptInput').value = activeAgentData.system_prompt || '';
                
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                
                Array.from(grid.children).forEach(c => c.classList.remove('active-card'));
                card.classList.add('active-card');
            });
            grid.appendChild(card);
        });
        
        // Add create handler
        const createBtn = document.getElementById('projectCreateNewBtn');
        if (createBtn && !createBtn.hasAttribute('data-bound')) {
            createBtn.setAttribute('data-bound', 'true');
            createBtn.addEventListener('click', async () => {
                const res = await authFetch('/api/agents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_id: projectId,
                        name: "New Custom Agent",
                        description: "A fresh agent ready to be configured",
                        system_prompt: "You are a helpful AI agent."
                    })
                });
                const newAgent = await res.json();
                activeAgentId = newAgent.id;
                activeAgentData = newAgent;
                loadProjectAgentsList();
                
                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
            });
        }
    } catch (e) {
        console.error("Error loading project agents list:", e);
    }
}
"""

if "async function loadProjectAgentsList" not in content:
    content += "\n" + agents_list_func

# 5. Fix agentId to activeAgentId replacements globally where required
content = content.replace("`/api/agents/${agentId}`", "`/api/agents/${activeAgentId}`")
content = content.replace("agentData.connected_tools", "activeAgentData.connected_tools")
content = content.replace("`/api/agents/${agentId}/tools`", "`/api/agents/${activeAgentId}/tools`")
content = content.replace("agentData.llm_config_id", "(activeAgentData ? activeAgentData.llm_config_id : null)")
content = content.replace("`/api/agents/${agentId}/llm`", "`/api/agents/${activeAgentId}/llm`")
content = content.replace("`/api/knowledge/${agentId}`", "`/api/knowledge/${activeAgentId}`")
content = content.replace("formData.append('agent_id', agentId);", "formData.append('agent_id', activeAgentId);")

content = content.replace("agentData.name || ''", "activeAgentData.name || ''")
content = content.replace("agentData.description || ''", "activeAgentData.description || ''")
content = content.replace("agentData.system_prompt || ''", "activeAgentData.system_prompt || ''")

content = content.replace("`/api/workflows?agent_id=${agentId}`", "`/api/workflows?project_id=${projectId}&agent_id=${activeAgentId || ''}`")
content = content.replace("agent_id=${agentId}&t=${Date.now()}", "project_id=${projectId}&agent_id=${activeAgentId || ''}&t=${Date.now()}")
content = content.replace("workflow_id=${encodeURIComponent(filterWorkflow)}&status=${encodeURIComponent(filterStatus)}&t=${Date.now()}", "project_id=${projectId}&workflow_id=${encodeURIComponent(filterWorkflow)}&status=${encodeURIComponent(filterStatus)}&t=${Date.now()}")

content = content.replace("agent_id: agentId, title", "project_id: projectId, agent_id: activeAgentId || null, title")
content = content.replace("`/api/chat/threads?agent_id=${agentId}`", "`/api/chat/threads?project_id=${projectId}`")

content = content.replace("""        agent_id: agentId,
        thread_id: currentThreadId,""", """        project_id: projectId,
        agent_id: activeAgentId,
        thread_id: currentThreadId,""")

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Project JS Patched successfully!")
