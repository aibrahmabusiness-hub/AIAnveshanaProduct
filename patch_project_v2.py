import re
import os

filepath = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State Variables
content = content.replace(
    "const agentId = parseInt(pathParts[pathParts.length - 1]);\nlet agentData = null;",
    "const projectId = parseInt(pathParts[pathParts.length - 1]);\nlet projectData = null;\nlet activeAgentId = null;\nlet activeAgentData = null;"
)

# 2. init() function
init_search = """async function init() {
    // Load agent info
    const res = await authFetch(`/api/agents/${agentId}`);
    agentData = await res.json();
    document.getElementById('sidebarTitle').textContent = agentData.name;
    document.title = `${agentData.name} - Workspace`;

    const toolCount = (agentData.connected_tools || []).length;
    document.getElementById('connectedToolsBadge').textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;"""
init_replace = """async function init() {
    // Load project info
    const res = await authFetch(`/api/projects/${projectId}`);
    const data = await res.json();
    projectData = data.project;
    document.getElementById('sidebarTitle').textContent = projectData.name;
    document.title = `${projectData.name} - Workspace`;

    // Wait for agents list to update badge
"""
content = content.replace(init_search, init_replace)

# 3. View Routing (switchView and DOMContentLoaded)
view_search = """    if (viewId === 'view-agents') {
        if (window.location.hash.includes('agents-config')) {
            document.getElementById('agents-list-screen').style.display = 'none';
            document.getElementById('agent-config-screen').style.display = 'flex';
            
            setTimeout(() => {
                if (agentData) {
                    document.getElementById('configAgentTitle').textContent = `Configuring: ${agentData.name}`;
                    // Populate basic form fields if they exist
                    if(document.getElementById('agentNameInput')) document.getElementById('agentNameInput').value = agentData.name;
                    if(document.getElementById('agentDescInput')) document.getElementById('agentDescInput').value = agentData.description;
                    if(document.getElementById('personalityPromptInput')) document.getElementById('personalityPromptInput').value = agentData.system_prompt || '';
                }
            }, 500);
        } else {
            document.getElementById('agent-config-screen').style.display = 'none';
            document.getElementById('agents-list-screen').style.display = 'flex';
        }
    }"""
view_replace = """    if (viewId === 'view-agents') {
        if (window.location.hash.includes('agents-config') && activeAgentId) {
            document.getElementById('agents-list-screen').style.display = 'none';
            document.getElementById('agent-config-screen').style.display = 'flex';
            
            setTimeout(() => {
                if (activeAgentData) {
                    document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                    // Populate basic form fields if they exist
                    if(document.getElementById('agentNameInput')) document.getElementById('agentNameInput').value = activeAgentData.name;
                    if(document.getElementById('agentDescInput')) document.getElementById('agentDescInput').value = activeAgentData.description;
                    if(document.getElementById('personalityPromptInput')) document.getElementById('personalityPromptInput').value = activeAgentData.system_prompt || '';
                }
            }, 500);
        } else {
            document.getElementById('agent-config-screen').style.display = 'none';
            document.getElementById('agents-list-screen').style.display = 'block';
        }
    }"""
content = content.replace(view_search, view_replace)

domcontent_search = """// Setup Agent Config Switch
document.addEventListener("DOMContentLoaded", () => {
    // Check initial hash
    if(window.location.hash.includes('agents-config')) {
        switchView('view-agents');
    }

    // Back to agents list button
    const backBtn = document.getElementById('backToAgentsListBtn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            document.getElementById('agent-config-screen').style.display = 'none';
            document.getElementById('agents-list-screen').style.display = 'flex';
            history.pushState("", document.title, window.location.pathname + window.location.search);
        });
    }

    // Create New Custom Agent
    const createBtn = document.getElementById('projectCreateNewBtn');
    if (createBtn) {
        createBtn.addEventListener('click', async () => {
            try {
                const res = await authFetch('/api/agents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: "New Custom Agent",
                        description: "A fresh agent ready to be configured",
                        system_prompt: "You are a helpful AI agent."
                    })
                });
                const newAgent = await res.json();
                // Select this new agent and go to config
                window.location.href = `/project/${newAgent.id}#agents-config`;
                window.location.reload();
            } catch (err) {
                console.error("Error creating custom agent", err);
            }
        });
    }
});"""
domcontent_replace = """// Setup Agent Config Switch
document.addEventListener("DOMContentLoaded", () => {
    // Check initial hash
    if(window.location.hash.includes('agents-config')) {
        // Handled in loadProjectAgentsList
    }

    // Back to agents list button
    const backBtn = document.getElementById('backToAgentsListBtn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            document.getElementById('agent-config-screen').style.display = 'none';
            document.getElementById('agents-list-screen').style.display = 'block';
            history.pushState("", document.title, window.location.pathname + window.location.search);
        });
    }

    // Create New Custom Agent
    const createBtn = document.getElementById('projectCreateNewBtn');
    if (createBtn) {
        createBtn.addEventListener('click', async () => {
            try {
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
                window.location.hash = `#agents-config-${newAgent.id}`;
                switchView('view-agents');
                loadProjectAgentsList();
            } catch (err) {
                console.error("Error creating custom agent", err);
            }
        });
    }
});"""
content = content.replace(domcontent_search, domcontent_replace)

# 4. loadProjectAgentsList
load_agents_search = """async function loadProjectAgentsList() {
    try {
        const res = await authFetch('/api/agents');
        if (!res.ok) throw new Error('Failed to fetch agents');
        const data = await res.json();
        
        const grid = document.getElementById('projectAgentsGrid');
        if (!grid) return;

        // Keep the first two fixed cards, remove dynamically added ones
        const cards = Array.from(grid.children);
        cards.slice(2).forEach(c => c.remove());
        
        data.agents.forEach(agent => {
            const card = document.createElement('div');
            card.className = 'agent-hub-card';
            if (agent.id === agentId) {
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
                        <div class="tool-box"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg></div>
                        <div class="tool-box"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg></div>
                        <div class="tool-box count">+${toolCount}</div>
                    </div>
                    <div class="nav-arrow">↗</div>
                </div>
            `;
            card.addEventListener('click', () => {
                window.location.href = `/project/${agent.id}#agents-config`;
                window.location.reload();
            });
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading project agents list:", e);
    }
}"""
load_agents_replace = """async function loadProjectAgentsList() {
    try {
        const res = await authFetch(`/api/projects/${projectId}/agents`);
        if (!res.ok) throw new Error('Failed to fetch agents');
        const data = await res.json();
        
        const grid = document.getElementById('projectAgentsGrid');
        if (!grid) return;

        // Keep the first two fixed cards, remove dynamically added ones
        const cards = Array.from(grid.children);
        cards.slice(2).forEach(c => c.remove());
        
        document.getElementById('connectedToolsBadge').textContent = `${data.agents.length} agent${data.agents.length !== 1 ? 's' : ''}`;

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
                        <div class="tool-box"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg></div>
                        <div class="tool-box"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg></div>
                        <div class="tool-box count">+${toolCount}</div>
                    </div>
                    <div class="nav-arrow">↗</div>
                </div>
            `;
            card.addEventListener('click', async () => {
                activeAgentId = agent.id;
                const agentRes = await authFetch(`/api/agents/${activeAgentId}`);
                activeAgentData = await agentRes.json();
                window.location.hash = `#agents-config-${activeAgentId}`;
                switchView('view-agents');
                Array.from(grid.children).forEach(c => c.classList.remove('active-card'));
                card.classList.add('active-card');
            });
            grid.appendChild(card);
        });

        if(window.location.hash.startsWith('#agents-config-')) {
            const hashId = parseInt(window.location.hash.replace('#agents-config-', ''));
            if(hashId) {
                activeAgentId = hashId;
                const agentRes = await authFetch(`/api/agents/${activeAgentId}`);
                activeAgentData = await agentRes.json();
                switchView('view-agents');
            }
        }
    } catch (e) {
        console.error("Error loading project agents list:", e);
    }
}"""
content = content.replace(load_agents_search, load_agents_replace)

# 5. Agent Settings (PUT)
content = content.replace("name: document.getElementById('agentNameInput').value,", "project_id: projectId,\n            name: document.getElementById('agentNameInput').value,")
content = content.replace("`/api/agents/${agentId}`", "`/api/agents/${activeAgentId}`")

# 6. Tools, LLM, Knowledge Base, Workflows
content = content.replace("if (!agentData) return;", "if (!activeAgentData) return;")
content = content.replace("agentData =", "activeAgentData =")
content = content.replace("agentData.connected_tools", "activeAgentData.connected_tools")
content = content.replace("`/api/knowledge/${agentId}`", "`/api/knowledge/${activeAgentId}`")
content = content.replace("formData.append('agent_id', agentId);", "formData.append('agent_id', activeAgentId);")
content = content.replace("`/api/agents/${agentId}/tools`", "`/api/agents/${activeAgentId}/tools`")
content = content.replace("`/api/agents/${agentId}/llm`", "`/api/agents/${activeAgentId}/llm`")
content = content.replace("agentData.llm_config_id", "(activeAgentData && activeAgentData.llm_config_id)")
content = content.replace("`/api/workflows?agent_id=${agentId}&t=${Date.now()}`", "`/api/workflows?agent_id=${activeAgentId}&t=${Date.now()}`")

# 7. Chat Threads
content = content.replace("`/api/chat/threads?agent_id=${agentId}`", "`/api/chat/threads?project_id=${projectId}`")
content = content.replace("body: JSON.stringify({ agent_id: agentId, title })", "body: JSON.stringify({ agent_id: activeAgentId || null, project_id: projectId, title })")
content = content.replace("""        agent_id: agentId,
        thread_id: currentThreadId,""", """        agent_id: activeAgentId,
        project_id: projectId,
        thread_id: currentThreadId,""")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched successfully")
