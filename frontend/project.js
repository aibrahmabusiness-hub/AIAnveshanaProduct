// --- Authentication & Headers Helper ---
const token = localStorage.getItem('token');
const username = localStorage.getItem('username');

if (username) {
    document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();
    const dropdownUsername = document.getElementById('dropdownUsername');
    if (dropdownUsername) dropdownUsername.textContent = username;
}

// Profile dropdown toggle
const userAvatar = document.getElementById('userAvatar');
const profileDropdown = document.getElementById('profileDropdown');

if (userAvatar && profileDropdown) {
    userAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        profileDropdown.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!profileDropdown.contains(e.target) && e.target !== userAvatar) {
            profileDropdown.classList.remove('active');
        }
    });
}

// Dropdown Logout
const dropdownLogoutBtn = document.getElementById('dropdownLogoutBtn');
if (dropdownLogoutBtn) {
    dropdownLogoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/login';
    });
}

// Legacy logout button compatibility
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/login';
    });
}

async function authFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    if (!options.headers) options.headers = {};
    if (token) options.headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(API_BASE_URL + url, options);
    if (res.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/login';
    }
    return res;
}

// --- State ---
const pathParts = window.location.pathname.split('/');
const agentId = parseInt(pathParts[pathParts.length - 1]);
let agentData = null;
let llmConfigs = [];

// --- Init ---
async function init() {
    // Load agent info
    const res = await authFetch(`/api/agents/${agentId}`);
    agentData = await res.json();
    document.getElementById('sidebarTitle').textContent = agentData.name;
    document.title = `${agentData.name} - Workspace`;

    const toolCount = (agentData.connected_tools || []).length;
    document.getElementById('connectedToolsBadge').textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;

    // Load chat threads
    loadChatThreads();
    // Load tools view
    loadToolsView();
    // Load knowledge base
    loadKnowledgeBase();
    // Load settings view options
    loadSettingsView();
    // Load workflows view
    loadWorkflowsView();
}

// --- Sidebar Navigation ---
document.querySelectorAll('.ws-nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.ws-nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        const viewId = item.dataset.view;
        document.querySelectorAll('.ws-view').forEach(v => v.classList.remove('active'));
        document.getElementById(`view-${viewId}`).classList.add('active');

        // Show/hide history panel based on view
        const historyPanel = document.getElementById('historyPanel');
        historyPanel.style.display = viewId === 'chat' ? '' : 'none';
    });
});

// --- Chat & Threads ---
const promptInput = document.getElementById('promptInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const newThreadBtn = document.getElementById('newThreadBtn');

let activeThreadId = null;

// New Thread Button
newThreadBtn.addEventListener('click', async () => {
    await createNewThread();
});

async function createNewThread(initialPrompt = null) {
    const title = initialPrompt ? (initialPrompt.substring(0, 30) + (initialPrompt.length > 30 ? '...' : '')) : `Chat Session ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    try {
        const res = await authFetch('/api/chat/threads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_id: agentId, title })
        });
        const thread = await res.json();
        activeThreadId = thread.id;
        chatMessages.innerHTML = '';
        const greeting = document.getElementById('greetingText');
        if (greeting) greeting.style.display = 'block';
        await loadChatThreads();
    } catch (e) {
        console.error("Error creating thread:", e);
    }
}

async function loadChatThreads() {
    try {
        const res = await authFetch(`/api/chat/threads?agent_id=${agentId}`);
        const data = await res.json();
        const historyList = document.getElementById('historyList');
        
        if (!data.threads || data.threads.length === 0) {
            historyList.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:12px 0;">No threads yet. Click "+ New" to start a chat.</div>';
            activeThreadId = null;
            chatMessages.innerHTML = '';
            const greeting = document.getElementById('greetingText');
            if (greeting) greeting.style.display = 'block';
            return;
        }

        historyList.innerHTML = data.threads.map(t => `
            <div class="history-item ${t.id === activeThreadId ? 'active' : ''}" data-thread-id="${t.id}" style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-radius:6px; cursor:pointer;">
                <span class="thread-title" style="flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${t.title}</span>
                <button class="btn-delete delete-thread-btn" data-thread-id="${t.id}" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:0.85rem; padding:2px 6px;">✕</button>
            </div>
        `).join('');

        // Highlight active and bind click events
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-thread-btn')) {
                    e.stopPropagation();
                    deleteThread(parseInt(e.target.dataset.threadId));
                    return;
                }
                switchThread(parseInt(item.dataset.threadId));
            });
        });

        // Auto-select first thread if none active
        if (activeThreadId === null && data.threads.length > 0) {
            switchThread(data.threads[0].id);
        }
    } catch (e) {
        console.error("Error loading threads:", e);
    }
}

async function switchThread(threadId) {
    activeThreadId = threadId;
    
    // Highlight in sidebar
    document.querySelectorAll('.history-item').forEach(item => {
        if (parseInt(item.dataset.threadId) === threadId) {
            item.classList.add('active');
            item.style.backgroundColor = 'var(--primary-light)';
            item.style.color = 'var(--primary-color)';
        } else {
            item.classList.remove('active');
            item.style.backgroundColor = '';
            item.style.color = '';
        }
    });

    const greeting = document.getElementById('greetingText');
    if (greeting) greeting.style.display = 'none';

    chatMessages.innerHTML = '<span style="color:var(--text-muted); font-size:0.85rem;">Loading messages...</span>';

    try {
        const res = await authFetch(`/api/chat/threads/${threadId}/history`);
        const data = await res.json();
        chatMessages.innerHTML = '';
        
        if (data.history && data.history.length > 0) {
            let activeStageWrapper = null;
            data.history.forEach(m => {
                if (m.role === 'stage') {
                    try {
                        const stageData = JSON.parse(m.message);
                        if (!activeStageWrapper) {
                            const loadingId = `stage-hist-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
                            appendMessage('assistant', `
                                <div class="agent-stages-wrapper" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; width: 100%;"></div>
                                <div class="agent-final-response" style="display: none; border-top: 1px solid var(--border-color); padding-top: 10px; margin-top: 10px; font-size: 0.9rem; line-height: 1.6;"></div>
                            `, loadingId);
                            const loadingEl = document.getElementById(loadingId);
                            activeStageWrapper = {
                                container: loadingEl.querySelector('.agent-stages-wrapper'),
                                response: loadingEl.querySelector('.agent-final-response')
                            };
                        }
                        
                        const item = document.createElement('div');
                        let cssClass = 'analyzing';
                        let label = stageData.stage;
                        
                        if (stageData.tool) {
                            cssClass = 'tool-exec';
                            label = `🔧 Running integration: <strong style="color:var(--text-main); font-weight:600;">${stageData.tool}</strong>`;
                        } else if (stageData.stage.toLowerCase().includes('rag') || stageData.stage.toLowerCase().includes('knowledge')) {
                            cssClass = 'analyzing';
                            label = `🔍 Searching knowledge base...`;
                        } else if (stageData.stage.toLowerCase().includes('finalizing') || stageData.stage.toLowerCase().includes('answer')) {
                            cssClass = 'completed';
                        }
                        
                        item.className = `agent-stage-item completed`;
                        item.style.cssText = 'display: flex; align-items: center; gap: 10px; padding: 6px 12px; border-radius: 8px; background: #f0fdf4; border: 1px solid #dcfce7; font-size: 0.85rem; font-weight: 500; color: #16a34a; margin-top: 6px; width: max-content; max-width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.02);';
                        item.innerHTML = `
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="flex-shrink:0;"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            <span class="stage-label">${label}</span>
                        `;
                        activeStageWrapper.container.appendChild(item);
                    } catch (e) {
                        console.error("Error parsing history stage:", e);
                    }
                } else if (m.role === 'assistant') {
                    if (activeStageWrapper) {
                        activeStageWrapper.response.innerHTML = typeof window.marked !== 'undefined' ? window.marked.parse(m.message) : m.message;
                        activeStageWrapper.response.style.display = 'block';
                        activeStageWrapper = null;
                    } else {
                        appendMessage('assistant', m.message);
                    }
                } else {
                    appendMessage('user', m.message);
                    activeStageWrapper = null;
                }
            });
        } else {
            if (greeting) greeting.style.display = 'block';
        }
    } catch (e) {
        chatMessages.innerHTML = '<span style="color:#ef4444; font-size:0.85rem;">Error loading messages.</span>';
    }
}

async function deleteThread(threadId) {
    if (confirm("Are you sure you want to delete this chat thread?")) {
        try {
            await authFetch(`/api/chat/threads/${threadId}`, { method: 'DELETE' });
            if (activeThreadId === threadId) {
                activeThreadId = null;
            }
            await loadChatThreads();
        } catch (e) {
            console.error("Error deleting thread:", e);
        }
    }
}

async function sendMessage() {
    const prompt = promptInput.value.trim();
    if (!prompt) return;
    promptInput.value = '';

    // Auto-create thread if none exists/active
    if (activeThreadId === null) {
        await createNewThread(prompt);
    }

    // Hide greeting
    const greeting = document.getElementById('greetingText');
    if (greeting) greeting.style.display = 'none';

    // Show user message
    appendMessage('user', prompt);

    // Show thinking indicator/stage container
    const loadingId = `loading-${Date.now()}`;
    
    // Inject dynamic CSS keyframes if not existing
    if (!document.getElementById('spin-keyframes-style')) {
        const style = document.createElement('style');
        style.id = 'spin-keyframes-style';
        style.innerHTML = `
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .stage-spinner {
                animation: spin 1s linear infinite;
            }
            .agent-stage-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 6px 12px;
                border-radius: 8px;
                background: #fdfaf7;
                border: 1px solid #ffedd5;
                font-size: 0.85rem;
                font-weight: 500;
                color: #ea580c;
                transition: all 0.25s ease;
                margin-top: 6px;
                width: max-content;
                max-width: 100%;
                box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            }
            .agent-stage-item.completed {
                background: #f0fdf4;
                border-color: #dcfce7;
                color: #16a34a;
            }
            .agent-stage-item.active {
                border-color: #fca5a5;
                background: #fff5f5;
                color: #e11d48;
            }
            .agent-stage-item.analyzing {
                background: #eff6ff;
                border-color: #dbeafe;
                color: #2563eb;
            }
            .agent-stage-item.tool-exec {
                background: #faf5ff;
                border-color: #f3e8ff;
                color: #7c3aed;
                border-style: dashed;
                border-width: 1.5px;
            }
        `;
        document.head.appendChild(style);
    }

    appendMessage('assistant', `
        <div class="agent-stages-wrapper" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; width: 100%;">
            <div class="agent-stage-item analyzing" id="${loadingId}-thinking">
                <div class="stage-spinner" style="width: 14px; height: 14px; border: 2px solid currentColor; border-top-color: transparent; border-radius: 50%; flex-shrink: 0;"></div>
                <span class="stage-label">Thinking...</span>
            </div>
        </div>
        <div class="agent-final-response" style="display: none; border-top: 1px solid var(--border-color); padding-top: 10px; margin-top: 10px; font-size: 0.9rem; line-height: 1.6;"></div>
    `, loadingId);

    const loadingEl = document.getElementById(loadingId);
    const stagesContainer = loadingEl.querySelector('.agent-stages-wrapper');
    const finalResponseEl = loadingEl.querySelector('.agent-final-response');

    function updateStages(stageName, toolName) {
        // Mark all existing active stages as completed
        stagesContainer.querySelectorAll('.agent-stage-item').forEach(item => {
            if (!item.classList.contains('completed')) {
                item.classList.remove('analyzing', 'tool-exec');
                item.classList.add('completed');
                const spinner = item.querySelector('.stage-spinner');
                if (spinner) {
                    spinner.outerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="flex-shrink:0;"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                }
            }
        });

        // Add new stage
        const item = document.createElement('div');
        let cssClass = 'analyzing';
        let label = stageName;
        
        if (toolName) {
            cssClass = 'tool-exec';
            label = `🔧 Running integration: <strong style="color:var(--text-main); font-weight:600;">${toolName}</strong>`;
        } else if (stageName.toLowerCase().includes('rag') || stageName.toLowerCase().includes('knowledge')) {
            cssClass = 'analyzing';
            label = `🔍 Searching knowledge base...`;
        } else if (stageName.toLowerCase().includes('finalizing') || stageName.toLowerCase().includes('answer')) {
            cssClass = 'completed';
        }

        item.className = `agent-stage-item ${cssClass}`;
        
        if (cssClass === 'completed') {
            item.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="flex-shrink:0;"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span class="stage-label">${label}</span>
            `;
        } else {
            item.innerHTML = `
                <div class="stage-spinner" style="width: 14px; height: 14px; border: 2px solid currentColor; border-top-color: transparent; border-radius: 50%; flex-shrink: 0;"></div>
                <span class="stage-label">${label}</span>
            `;
        }

        stagesContainer.appendChild(item);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    try {
        const res = await authFetch(`/api/chat/threads/${activeThreadId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!res.ok) {
            throw new Error(`Server returned status ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalReply = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const eventData = JSON.parse(line);
                    if (eventData.type === 'stage') {
                        updateStages(eventData.stage, eventData.tool);
                    } else if (eventData.type === 'reply') {
                        finalReply = eventData.reply;
                    } else if (eventData.type === 'error') {
                        finalReply = `<span style="color:#ef4444;">Error: ${eventData.message}</span>`;
                    }
                } catch (err) {
                    console.error("Stream parse error:", err, line);
                }
            }
        }

        // Finalize all stages to completed state
        stagesContainer.querySelectorAll('.agent-stage-item').forEach(item => {
            item.className = 'agent-stage-item completed';
            const spinner = item.querySelector('.stage-spinner');
            if (spinner) {
                spinner.outerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="flex-shrink:0;"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
            }
        });

        // Set response
        finalResponseEl.innerHTML = typeof window.marked !== 'undefined' ? window.marked.parse(finalReply || 'No reply generated.') : (finalReply || 'No reply generated.');
        finalResponseEl.style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (e) {
        stagesContainer.innerHTML = `<div style="color:#ef4444; font-size:0.85rem; font-weight:600;">⚠️ Connection Failed: ${e.message}</div>`;
    }
}


function appendMessage(role, text, id) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    if (id) div.id = id;
    
    let processedText = text;
    if (role === 'assistant') {
        if (typeof window.marked !== 'undefined' && !text.includes('agent-stages-wrapper')) {
            processedText = window.marked.parse(text);
        }
    }
    
    div.innerHTML = `
        <div class="msg-avatar">${role === 'user' ? 'You' : 'AI'}</div>
        <div class="msg-text">${processedText}</div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
promptInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

// --- Tools View ---
async function loadToolsView() {
    const res = await authFetch('/api/tools');
    const data = await res.json();
    const toolsList = document.getElementById('toolsList');
    const connected = agentData.connected_tools || [];

    // Define groups
    const groups = [
        {
            id: 'servicenow',
            name: 'ServiceNow Integration',
            tools: ['servicenow_incidents', 'servicenow_tables']
        },
        {
            id: 'salesforce',
            name: 'Salesforce CRM Integration',
            tools: ['salesforce_query', 'salesforce_create']
        },
        {
            id: 'gmail',
            name: 'Gmail Suite Integration',
            tools: ['gmail_read', 'gmail_send']
        },
        {
            id: 'jira',
            name: 'Atlassian Jira Integration',
            tools: ['jira_issues']
        },
        {
            id: 'outlook',
            name: 'Microsoft Outlook (System default)',
            tools: ['outlook_calendar', 'outlook_email'],
            systemDefault: true
        },
        {
            id: 'google_search_tool',
            name: 'Web Search Capabilities (System default)',
            tools: ['google_search'],
            systemDefault: true
        }
    ];

    // Query connection statuses
    const statuses = {};
    for (const group of groups) {
        if (group.systemDefault) {
            statuses[group.id] = true;
            continue;
        }
        try {
            const statusRes = await authFetch(`/api/credentials/${group.id}`);
            const statusData = await statusRes.json();
            statuses[group.id] = statusData.configured;
        } catch (err) {
            statuses[group.id] = false;
        }
    }

    let html = '<div class="tools-groups-container">';

    for (const group of groups) {
        const isConnected = statuses[group.id];
        const statusBadgeClass = isConnected ? 'tools-group-badge connected' : 'tools-group-badge disconnected';
        const statusText = isConnected ? '● Connected' : 'Disconnected';
        
        // Find tool objects for this group
        const groupTools = data.tools.filter(t => group.tools.includes(t.id));

        html += `
            <div class="tools-group-card">
                <div class="tools-group-header">
                    <div class="tools-group-title">
                        <strong>${group.name}</strong>
                    </div>
                    <span class="${statusBadgeClass}">${statusText}</span>
                </div>
                ${!isConnected ? `
                    <div style="background:#fef2f2; border:1px solid #fca5a5; color:#b91c1c; font-size:0.8rem; padding:8px 12px; border-radius:6px; margin-bottom:12px;">
                        ⚠️ This integration is not connected. Configure credentials under <strong>Settings</strong> to enable these capabilities.
                    </div>
                ` : ''}
                <div class="tools-capabilities-grid">
                    ${groupTools.map(tool => {
                        const isChecked = connected.includes(tool.id) ? 'checked' : '';
                        const isDisabled = !isConnected ? 'disabled' : '';
                        return `
                            <div class="tools-capability-card" style="${!isConnected ? 'opacity: 0.6; cursor: not-allowed;' : ''}">
                                <input type="checkbox" class="tools-capability-checkbox" name="agentTools" value="${tool.id}" ${isChecked} ${isDisabled}>
                                <div class="tools-capability-info">
                                    <span class="tools-capability-name">${tool.name}</span>
                                    <span class="tools-capability-desc">${tool.description}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    html += '</div>';
    toolsList.innerHTML = html;

    // Bind save
    document.getElementById('saveToolsBtn').replaceWith(document.getElementById('saveToolsBtn').cloneNode(true));
    document.getElementById('saveToolsBtn').addEventListener('click', async () => {
        const selected = [...document.querySelectorAll('input[name="agentTools"]:checked')].map(cb => cb.value);
        await authFetch(`/api/agents/${agentId}/tools`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ connected_tools: selected })
        });
        agentData.connected_tools = selected;
        const toolCount = selected.length;
        document.getElementById('connectedToolsBadge').textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
        alert('Tools saved!');
    });
}

// --- Knowledge Base ---
async function loadKnowledgeBase() {
    const res = await authFetch(`/api/knowledge/${agentId}`);
    const data = await res.json();
    const docsList = document.getElementById('kbDocsList');

    if (!data.documents || data.documents.length === 0) {
        docsList.innerHTML = '<p style="color:var(--text-muted); font-size:0.85rem;">No documents uploaded yet.</p>';
        return;
    }

    docsList.innerHTML = data.documents.map(doc => `
        <div class="kb-doc-row">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            <span>${doc.filename}</span>
            <button class="btn-delete" onclick="deleteDoc(${doc.id})">✕</button>
        </div>
    `).join('');
}

document.getElementById('kbFileInput').replaceWith(document.getElementById('kbFileInput').cloneNode(true));
document.getElementById('kbFileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    
    await authFetch(`/api/knowledge/${agentId}`, {
        method: 'POST',
        body: formData
    });
    loadKnowledgeBase();
    e.target.value = '';
});

async function deleteDoc(kbId) {
    if (confirm('Delete this knowledge document?')) {
        await authFetch(`/api/knowledge/${kbId}`, { method: 'DELETE' });
        loadKnowledgeBase();
    }
}

// --- Settings (LLM Keys & Credentials) ---

async function loadSettingsView() {
    // 1. Load LLM configurations
    const llmRes = await authFetch('/api/settings/llm');
    const llmData = await llmRes.json();
    llmConfigs = llmData.configs || [];

    const select = document.getElementById('agentLlmSelect');
    select.innerHTML = '<option value="">Default System Gemini</option>';
    llmConfigs.forEach(conf => {
        const selected = agentData.llm_config_id === conf.id ? 'selected' : '';
        select.innerHTML += `<option value="${conf.id}" ${selected}>${conf.provider.toUpperCase()} (${conf.model_name})</option>`;
    });

    // Showcase user LLMs dynamically in Agent General config too
    populateAgentModelDropdown();

    const configsList = document.getElementById('llmConfigsList');
    if (llmConfigs.length === 0) {
        configsList.innerHTML = '<p style="color:var(--text-muted); font-size:0.8rem;">No keys added yet.</p>';
    } else {
        configsList.innerHTML = llmConfigs.map(conf => `
            <div style="display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color); border-radius:6px; padding:10px 14px; font-size:0.85rem;">
                <div>
                    <strong>${conf.provider.toUpperCase()}</strong>: <code>${conf.model_name}</code>
                    <span style="color:var(--text-muted); margin-left:10px;">${conf.api_key_masked}</span>
                    ${conf.is_default ? '<span style="color:var(--primary-color); font-weight:600; margin-left:8px;">[Default]</span>' : ''}
                </div>
                <div style="display:flex; gap:8px;">
                    ${!conf.is_default ? `<button class="btn-cancel" onclick="setDefaultLlm(${conf.id})" style="padding:4px 8px; font-size:0.75rem;">Set Default</button>` : ''}
                    <button class="btn-delete" onclick="deleteLlmConfig(${conf.id})" style="padding:4px 8px; font-size:0.75rem;">✕</button>
                </div>
            </div>
        `).join('');
    }

    // Sync status badges for integrations
    const integrations = ['servicenow', 'gmail', 'salesforce', 'jira'];
    for (const app of integrations) {
        try {
            const statusRes = await authFetch(`/api/credentials/${app}`);
            const statusData = await statusRes.json();
            const badge = document.getElementById(`badge-${app}`);
            if (badge) {
                if (statusData.configured) {
                    badge.textContent = "● Connected";
                    badge.style.color = "#16a34a"; // Green
                } else {
                    badge.textContent = "Disconnected";
                    badge.style.color = "var(--text-muted)";
                }
            }
            if (statusData.credentials) {
                const creds = statusData.credentials;
                if (app === 'servicenow') {
                    if (creds.instance_url) document.getElementById('snUrl').value = creds.instance_url;
                    if (creds.client_id) document.getElementById('snClientId').value = creds.client_id;
                    if (creds.client_secret) document.getElementById('snClientSecret').value = creds.client_secret;
                    if (creds.username) document.getElementById('snUser').value = creds.username;
                    if (creds.password) document.getElementById('snPass').value = creds.password;
                } else if (app === 'gmail') {
                    if (creds.username) document.getElementById('gmUser').value = creds.username;
                    if (creds.password) document.getElementById('gmToken').value = creds.password;
                } else if (app === 'salesforce') {
                    if (creds.instance_url) document.getElementById('sfUrl').value = creds.instance_url;
                    if (creds.username) document.getElementById('sfUser').value = creds.username;
                    if (creds.password) document.getElementById('sfPass').value = creds.password;
                    if (creds.security_token) document.getElementById('sfToken').value = creds.security_token;
                } else if (app === 'jira') {
                    if (creds.instance_url) document.getElementById('jrUrl').value = creds.instance_url;
                    if (creds.username) document.getElementById('jrUser').value = creds.username;
                    if (creds.password) document.getElementById('jrToken').value = creds.password;
                }
            }
        } catch (err) {
            console.error(`Error loading status for ${app}:`, err);
        }
    }
}

// Save Agent LLM Choice
document.getElementById('saveAgentLlmBtn').addEventListener('click', async () => {
    const configId = document.getElementById('agentLlmSelect').value;
    const llm_config_id = configId ? parseInt(configId) : null;
    await authFetch(`/api/agents/${agentId}/llm`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_config_id })
    });
    agentData.llm_config_id = llm_config_id;
    // Sync agent model dropdown too
    populateAgentModelDropdown();
    alert('Agent LLM updated!');
});

// Add new LLM Configuration
document.getElementById('addLlmConfigForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const provider = document.getElementById('llmProvider').value;
    const model_name = document.getElementById('llmModel').value;
    const api_key = document.getElementById('llmKey').value;

    await authFetch('/api/settings/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, model_name, api_key })
    });
    document.getElementById('llmModel').value = '';
    document.getElementById('llmKey').value = '';
    document.getElementById('llmTestStatus').style.display = 'none';
    loadSettingsView();
});

// Test LLM Connection
document.getElementById('testLlmConnBtn').addEventListener('click', async () => {
    const provider = document.getElementById('llmProvider').value;
    const model_name = document.getElementById('llmModel').value.trim();
    const api_key = document.getElementById('llmKey').value.trim();
    
    if (!model_name || !api_key) {
        alert('Please fill out model name and API key to test connection.');
        return;
    }
    
    const statusDiv = document.getElementById('llmTestStatus');
    statusDiv.style.display = 'block';
    statusDiv.style.backgroundColor = '#f3f4f6';
    statusDiv.style.color = '#4b5563';
    statusDiv.style.border = '1px solid #e5e7eb';
    statusDiv.textContent = 'Testing connection...';
    
    try {
        const res = await authFetch('/api/settings/llm/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, model_name, api_key })
        });
        const data = await res.json();
        if (data.status === 'success') {
            statusDiv.style.backgroundColor = '#ecfdf5';
            statusDiv.style.color = '#065f46';
            statusDiv.style.border = '1px solid #a7f3d0';
            statusDiv.textContent = data.message;
        } else {
            statusDiv.style.backgroundColor = '#fef2f2';
            statusDiv.style.color = '#991b1b';
            statusDiv.style.border = '1px solid #fca5a5';
            statusDiv.textContent = data.message;
        }
    } catch (e) {
        statusDiv.style.backgroundColor = '#fef2f2';
        statusDiv.style.color = '#991b1b';
        statusDiv.style.border = '1px solid #fca5a5';
        statusDiv.textContent = 'Error testing connection: ' + e.message;
    }
});

async function setDefaultLlm(configId) {
    await authFetch(`/api/settings/llm/${configId}/default`, { method: 'POST' });
    loadSettingsView();
}

async function deleteLlmConfig(configId) {
    if (confirm('Delete this LLM key?')) {
        await authFetch(`/api/settings/llm/${configId}`, { method: 'DELETE' });
        loadSettingsView();
    }
}

// Credentials Test Helper
async function testCredentials(toolName, creds, statusDivId) {
    const statusDiv = document.getElementById(statusDivId);
    statusDiv.style.display = 'block';
    statusDiv.style.backgroundColor = '#f3f4f6';
    statusDiv.style.color = '#4b5563';
    statusDiv.style.border = '1px solid #e5e7eb';
    statusDiv.textContent = 'Testing connection...';

    try {
        const res = await authFetch('/api/credentials/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tool_name: toolName, credentials: creds })
        });
        const data = await res.json();
        if (data.status === 'success') {
            statusDiv.style.backgroundColor = '#ecfdf5';
            statusDiv.style.color = '#065f46';
            statusDiv.style.border = '1px solid #a7f3d0';
            statusDiv.textContent = data.message;

            // Auto-save credentials on successful test
            await authFetch('/api/credentials', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_name: toolName, credentials: creds })
            });

            // Update badge to connected
            const badge = document.getElementById(`badge-${toolName}`);
            if (badge) {
                badge.textContent = "● Connected";
                badge.style.color = "#16a34a"; // Green
            }
            return true;
        } else {
            statusDiv.style.backgroundColor = '#fef2f2';
            statusDiv.style.color = '#991b1b';
            statusDiv.style.border = '1px solid #fca5a5';
            statusDiv.textContent = data.message;
            return false;
        }
    } catch (e) {
        statusDiv.style.backgroundColor = '#fef2f2';
        statusDiv.style.color = '#991b1b';
        statusDiv.style.border = '1px solid #fca5a5';
        statusDiv.textContent = 'Error testing connection: ' + e.message;
        return false;
    }
}

// Salesforce credentials
document.getElementById('saveSfCreds').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('sfUrl').value,
        username: document.getElementById('sfUser').value,
        password: document.getElementById('sfPass').value,
        security_token: document.getElementById('sfToken').value,
    };
    await authFetch('/api/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: 'salesforce', credentials: creds })
    });
    const badge = document.getElementById('badge-salesforce');
    if (badge) {
        badge.textContent = "● Connected";
        badge.style.color = "#16a34a";
    }
    alert('Salesforce credentials saved!');
});

document.getElementById('testSfCredsBtn').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('sfUrl').value,
        username: document.getElementById('sfUser').value,
        password: document.getElementById('sfPass').value,
        security_token: document.getElementById('sfToken').value,
    };
    await testCredentials('salesforce', creds, 'sfTestStatus');
});

// ServiceNow credentials
document.getElementById('saveSnCreds').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('snUrl').value,
        client_id: document.getElementById('snClientId').value,
        client_secret: document.getElementById('snClientSecret').value,
        username: document.getElementById('snUser').value,
        password: document.getElementById('snPass').value,
    };
    await authFetch('/api/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: 'servicenow', credentials: creds })
    });
    const badge = document.getElementById('badge-servicenow');
    if (badge) {
        badge.textContent = "● Connected";
        badge.style.color = "#16a34a";
    }
    alert('ServiceNow credentials saved!');
});

document.getElementById('testSnCredsBtn').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('snUrl').value,
        client_id: document.getElementById('snClientId').value,
        client_secret: document.getElementById('snClientSecret').value,
        username: document.getElementById('snUser').value,
        password: document.getElementById('snPass').value,
    };
    await testCredentials('servicenow', creds, 'snTestStatus');
});

// Settings blocks tab switcher
document.querySelectorAll('.settings-block-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.settings-block-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        
        const target = card.dataset.settingsTarget;
        document.querySelectorAll('.settings-config-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`settings-panel-${target}`).classList.add('active');
    });
});

// Gmail credentials
document.getElementById('saveGmCreds').addEventListener('click', async () => {
    const creds = {
        username: document.getElementById('gmUser').value,
        password: document.getElementById('gmToken').value,
        configured: true
    };
    await authFetch('/api/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: 'gmail', credentials: creds })
    });
    const badge = document.getElementById('badge-gmail');
    if (badge) {
        badge.textContent = "● Connected";
        badge.style.color = "#16a34a";
    }
    alert('Gmail credentials saved!');
});

document.getElementById('testGmCredsBtn').addEventListener('click', async () => {
    const creds = {
        username: document.getElementById('gmUser').value,
        password: document.getElementById('gmToken').value,
        configured: true
    };
    await testCredentials('gmail', creds, 'gmTestStatus');
});

// Jira credentials
document.getElementById('saveJrCreds').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('jrUrl').value,
        username: document.getElementById('jrUser').value,
        password: document.getElementById('jrToken').value,
    };
    await authFetch('/api/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: 'jira', credentials: creds })
    });
    const badge = document.getElementById('badge-jira');
    if (badge) {
        badge.textContent = "● Connected";
        badge.style.color = "#16a34a";
    }
    alert('Jira credentials saved!');
});

document.getElementById('testJrCredsBtn').addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('jrUrl').value,
        username: document.getElementById('jrUser').value,
        password: document.getElementById('jrToken').value,
    };
    await testCredentials('jira', creds, 'jrTestStatus');
});

// --- Workflows View & Modal Creation ---

const workflowModal = document.getElementById('workflowModal');
const closeWorkflowModalBtn = document.getElementById('closeWorkflowModalBtn');
const cancelWorkflowModalBtn = document.getElementById('cancelWorkflowModalBtn');
const createWorkflowForm = document.getElementById('createWorkflowForm');
const workflowStepsList = document.getElementById('workflowStepsList');
const addStepBtn = document.getElementById('addStepBtn');

document.getElementById('createNewWorkflowBtn').addEventListener('click', () => {
    workflowStepsList.innerHTML = '';
    addStepRow(); // Start with one empty step
    workflowModal.classList.add('active');
});

closeWorkflowModalBtn.addEventListener('click', () => workflowModal.classList.remove('active'));
cancelWorkflowModalBtn.addEventListener('click', () => workflowModal.classList.remove('active'));

const AVAILABLE_TOOLS = [
    { id: "gmail_send", name: "Gmail Send Email", params: ["to", "subject", "body"] },
    { id: "outlook_calendar", name: "Outlook Schedule Meeting", params: ["subject", "attendees", "start_time"] },
    { id: "salesforce_create", name: "Salesforce Create Record", params: ["object_type", "data"] }
];

function addStepRow() {
    const stepIdx = workflowStepsList.children.length + 1;
    const div = document.createElement('div');
    div.style.cssText = 'border:1px solid var(--border-color); border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:8px; background:#fafafa;';
    div.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>Step ${stepIdx}</strong>
            <button type="button" class="btn-delete" onclick="this.closest('div.step-row-container').remove(); reorderSteps();" style="font-size:0.75rem; padding:2px 6px;">Remove</button>
        </div>
        <div style="display:grid; grid-template-columns:1fr 2fr; gap:10px;">
            <select class="step-tool-select" style="padding:8px; border:1px solid var(--border-color); border-radius:6px; font-family:inherit;">
                ${AVAILABLE_TOOLS.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
            </select>
            <div class="step-params-container" style="display:flex; flex-direction:column; gap:6px;">
                <!-- Params inputs loaded here -->
            </div>
        </div>
    `;
    div.classList.add('step-row-container');
    workflowStepsList.appendChild(div);

    const select = div.querySelector('.step-tool-select');
    select.addEventListener('change', () => loadStepParams(div, select.value));
    loadStepParams(div, select.value);
}

function loadStepParams(containerDiv, toolId) {
    const paramsDiv = containerDiv.querySelector('.step-params-container');
    const tool = AVAILABLE_TOOLS.find(t => t.id === toolId);
    paramsDiv.innerHTML = tool.params.map(p => `
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:0.75rem; font-weight:500; min-width:80px;">${p}</span>
            <input type="text" class="step-param-input" data-param="${p}" placeholder="e.g. {{employee_${p}}} or values" style="flex:1; padding:6px 10px; border:1px solid var(--border-color); border-radius:4px; font-size:0.8rem; font-family:inherit;">
        </div>
    `).join('');
}

addStepBtn.addEventListener('click', addStepRow);

function reorderSteps() {
    [...workflowStepsList.children].forEach((div, idx) => {
        div.querySelector('strong').textContent = `Step ${idx + 1}`;
    });
}

// Save Workflow
createWorkflowForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('workflowName').value;
    const steps = [];

    [...workflowStepsList.children].forEach((div, idx) => {
        const tool = div.querySelector('.step-tool-select').value;
        const params = {};
        div.querySelectorAll('.step-param-input').forEach(inp => {
            params[inp.dataset.param] = inp.value;
        });
        steps.push({ order: idx + 1, tool, params });
    });

    await authFetch('/api/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId, name, steps })
    });

    workflowModal.classList.remove('active');
    loadWorkflowsView();
});

// Load Workflows
async function loadWorkflowsView() {
    const res = await authFetch(`/api/workflows?agent_id=${agentId}`);
    const data = await res.json();
    const workflowsList = document.getElementById('workflowsList');

    if (!data.workflows || data.workflows.length === 0) {
        workflowsList.innerHTML = '<p style="color:var(--text-muted); font-size:0.85rem;">No workflows configured for this agent yet.</p>';
        return;
    }

    workflowsList.innerHTML = data.workflows.map(wf => `
        <div style="border:1px solid var(--border-color); border-radius:12px; padding:20px; display:flex; justify-content:space-between; align-items:center; background:white; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div>
                <strong style="font-size:1rem; color:var(--text-main);">${wf.name}</strong>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">${wf.steps.length} step${wf.steps.length !== 1 ? 's' : ''}: ${wf.steps.map(s => s.tool).join(' ➔ ')}</div>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="openExecWorkflow(${wf.id})" style="padding:6px 12px; font-size:0.8rem;">Run</button>
                <button class="btn-cancel" onclick="deleteWorkflow(${wf.id})" style="padding:6px 12px; font-size:0.8rem; border:1px solid #ef4444; color:#ef4444; background:none;">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteWorkflow(wfId) {
    if (confirm('Delete this workflow?')) {
        await authFetch(`/api/workflows/${wfId}`, { method: 'DELETE' });
        loadWorkflowsView();
    }
}

// Execute Workflow Dialog
const execModal = document.getElementById('executeWorkflowModal');
const execFieldsList = document.getElementById('execFieldsList');
const execResultPanel = document.getElementById('execResultPanel');
const execResultLog = document.getElementById('execResultLog');
const executeWorkflowForm = document.getElementById('executeWorkflowForm');

async function openExecWorkflow(wfId) {
    document.getElementById('execWorkflowId').value = wfId;
    execResultPanel.style.display = 'none';
    
    // Fetch workflow step data to find placeholders
    const res = await authFetch(`/api/workflows/${wfId}`);
    const wf = await res.json();
    
    // Regex scan for {{variable}}
    const placeholders = new Set();
    wf.steps.forEach(step => {
        const scan = (obj) => {
            if (typeof obj === 'string') {
                const matches = obj.match(/\{\{([^}]+)\}\}/g);
                if (matches) {
                    matches.forEach(m => placeholders.add(m.slice(2, -2)));
                }
            } else if (typeof obj === 'object' && obj !== null) {
                Object.values(obj).forEach(scan);
            }
        };
        scan(step.params);
    });

    execFieldsList.innerHTML = '';
    if (placeholders.size === 0) {
        execFieldsList.innerHTML = '<p style="font-size:0.8rem; color:var(--text-muted);">No input parameters needed for this workflow.</p>';
    } else {
        [...placeholders].forEach(p => {
            execFieldsList.innerHTML += `
                <div class="form-group" style="margin-bottom:0;">
                    <label>${p}</label>
                    <input type="text" class="exec-input" data-var="${p}" required placeholder="Enter value for ${p}">
                </div>
            `;
        });
    }

    execModal.classList.add('active');
}

document.getElementById('closeExecModalBtn').addEventListener('click', () => execModal.classList.remove('active'));
document.getElementById('cancelExecModalBtn').addEventListener('click', () => execModal.classList.remove('active'));

executeWorkflowForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const wfId = document.getElementById('execWorkflowId').value;
    const input_data = {};
    execFieldsList.querySelectorAll('.exec-input').forEach(inp => {
        input_data[inp.dataset.var] = inp.value;
    });

    const startBtn = document.getElementById('startExecBtn');
    startBtn.textContent = 'Running...';
    startBtn.disabled = true;

    try {
        const res = await authFetch(`/api/workflows/${wfId}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data })
        });
        const data = await res.json();
        
        execResultLog.textContent = JSON.stringify(data, null, 2);
        execResultPanel.style.display = 'block';
    } catch (err) {
        execResultLog.textContent = `Execution failed: ${err.message}`;
        execResultPanel.style.display = 'block';
    } finally {
        startBtn.textContent = 'Run Flow';
        startBtn.disabled = false;
    }
});

async function loadAgentIntegrationsView() {
    const res = await authFetch('/api/tools');
    const data = await res.json();
    const listContainer = document.getElementById('agentIntegrationsList');
    if (!listContainer) return;
    
    const connected = agentData.connected_tools || [];

    const groups = [
        {
            id: 'servicenow',
            name: 'ServiceNow',
            desc: 'Incident creation & database table queries',
            tools: ['servicenow_incidents', 'servicenow_tables']
        },
        {
            id: 'salesforce',
            name: 'Salesforce CRM',
            desc: 'CRM record queries & lead/account creation',
            tools: ['salesforce_query', 'salesforce_create']
        },
        {
            id: 'gmail',
            name: 'Gmail Suite',
            desc: 'Standard email reading & communications sending',
            tools: ['gmail_read', 'gmail_send']
        },
        {
            id: 'jira',
            name: 'Atlassian Jira',
            desc: 'Issue creation, search queries, and comments tracking',
            tools: ['jira_issues']
        },
        {
            id: 'outlook',
            name: 'Microsoft Outlook (System)',
            desc: 'Emails reading/sending & Calendar meeting scheduling',
            tools: ['outlook_calendar', 'outlook_email'],
            systemDefault: true
        },
        {
            id: 'google_search_tool',
            name: 'Google Web Search',
            desc: 'Search the live web keylessly for real-time information and facts',
            tools: ['google_search'],
            systemDefault: true
        }
    ];

    const statuses = {};
    for (const group of groups) {
        if (group.systemDefault) {
            statuses[group.id] = true;
            continue;
        }
        try {
            const statusRes = await authFetch(`/api/credentials/${group.id}`);
            const statusData = await statusRes.json();
            statuses[group.id] = statusData.configured;
        } catch (err) {
            statuses[group.id] = false;
        }
    }

    listContainer.innerHTML = groups.map(group => {
        const isConnected = statuses[group.id];
        const badgeClass = isConnected ? 'agent-integration-badge connected' : 'agent-integration-badge unconfigured';
        const badgeText = isConnected ? 'Connected' : 'Not Configured';
        
        const groupTools = data.tools.filter(t => group.tools.includes(t.id));

        return `
            <div class="agent-integration-item" id="agent-int-item-${group.id}">
                <div class="agent-integration-summary">
                    <div class="agent-integration-title">
                        <strong>${group.name}</strong>
                        <span>${group.desc}</span>
                    </div>
                    <div class="agent-integration-actions">
                        <span class="${badgeClass}">${badgeText}</span>
                        ${!isConnected ? `
                            <button type="button" class="agent-connect-link" data-tool-target="${group.id}">Connect</button>
                        ` : `
                            <svg class="agent-expand-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        `}
                    </div>
                </div>
                <div class="agent-integration-details">
                    <div style="font-size:0.85rem; font-weight:600; color:var(--text-main); margin-bottom:10px;">Enable Capabilities for this Agent:</div>
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        ${groupTools.map(tool => {
                            const isChecked = connected.includes(tool.id) ? 'checked' : '';
                            return `
                                <label style="display:flex; align-items:flex-start; gap:10px; cursor:pointer;">
                                    <input type="checkbox" name="agentIntTools" value="${tool.id}" ${isChecked} style="margin-top:3px; accent-color:var(--orange-primary);">
                                    <div>
                                        <div style="font-size:0.85rem; font-weight:600; color:var(--text-main);">${tool.name}</div>
                                        <div style="font-size:0.75rem; color:var(--text-muted);">${tool.description}</div>
                                    </div>
                                </label>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    groups.forEach(group => {
        const itemEl = document.getElementById(`agent-int-item-${group.id}`);
        if (!itemEl) return;
        const summaryEl = itemEl.querySelector('.agent-integration-summary');
        const connectBtn = itemEl.querySelector('.agent-connect-link');
        
        if (statuses[group.id]) {
            summaryEl.addEventListener('click', (e) => {
                itemEl.classList.toggle('expanded');
            });
        }
        
        if (connectBtn) {
            connectBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const settingsNavItem = document.querySelector('.ws-nav-item[data-view="settings"]');
                if (settingsNavItem) {
                    settingsNavItem.click();
                }
                const card = document.querySelector(`.settings-block-card[data-settings-target="${group.id}"]`);
                if (card) {
                    card.click();
                }
            });
        }
    });

    document.querySelectorAll('input[name="agentIntTools"]').forEach(cb => {
        cb.addEventListener('change', async () => {
            const selectedTools = [...document.querySelectorAll('input[name="agentIntTools"]:checked')].map(c => c.value);
            await authFetch(`/api/agents/${agentId}/tools`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ connected_tools: selectedTools })
            });
            agentData.connected_tools = selectedTools;
            const toolCount = selectedTools.length;
            const badge = document.getElementById('connectedToolsBadge');
            if (badge) badge.textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
            updateAgentAttachedToolsBox();
        });
    });
}

async function updateAgentAttachedToolsBox() {
    const attachedBox = document.getElementById('agentAttachedTools');
    if (!attachedBox) return;

    try {
        const res = await authFetch('/api/tools');
        const data = await res.json();
        const connected = agentData.connected_tools || [];

        const activeTools = data.tools.filter(t => connected.includes(t.id));

        if (activeTools.length === 0) {
            attachedBox.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding: 10px 0;">No tools or capabilities attached.<br>Add integrations from the Integrations tab.</div>';
            return;
        }

        attachedBox.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:8px;">
                ${activeTools.map(t => `
                    <div style="display:flex; align-items:center; gap:8px; background:#fff7ed; border:1px solid #ffedd5; padding:8px 12px; border-radius:6px; color:#c2410c;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;">
                            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                        </svg>
                        <div style="font-size:0.8rem; font-weight:600;">${t.name}</div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (e) {
        console.error("Error loading attached tools:", e);
    }
}

// --- Agents Sub-tab Navigation & Configuration ---
function initAgentConfigForm() {
    // 1. Tab switching
    document.querySelectorAll('.agents-sub-item').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.agents-sub-item').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const targetTab = tab.dataset.agentTab;
            document.querySelectorAll('.agent-tab-view').forEach(view => {
                view.style.display = view.id === `agent-tab-${targetTab}` ? 'block' : 'none';
            });
            if (targetTab === 'integrations') {
                loadAgentIntegrationsView();
            }
        });
    });

    // Show/hide save button based on main view
    document.querySelectorAll('.ws-nav-item[data-view]').forEach(item => {
        item.addEventListener('click', () => {
            const viewId = item.dataset.view;
            document.getElementById('saveAgentBtn').style.display = viewId === 'agents' ? 'block' : 'none';
        });
    });
    // Trigger display check on init
    const activeMainView = document.querySelector('.ws-nav-item.active').dataset.view;
    document.getElementById('saveAgentBtn').style.display = activeMainView === 'agents' ? 'block' : 'none';

    // 2. Populate form fields
    document.getElementById('agentNameInput').value = agentData.name || '';
    const agentDescInput = document.getElementById('agentDescInput');
    if (agentDescInput) agentDescInput.value = agentData.description || '';
    document.getElementById('personalityPromptInput').value = agentData.system_prompt || '';
    document.getElementById('systemPromptConfigInput').value = agentData.system_prompt || '';
    document.getElementById('userPromptConfigInput').value = agentData.user_prompt || '';
    document.getElementById('maxToolCallsInput').value = agentData.max_tool_calls || 80;
    document.getElementById('guardrailsToggle').checked = agentData.guardrails !== false;
    document.getElementById('creativitySlider').value = agentData.creativity !== undefined ? agentData.creativity : 0.5;
    document.getElementById('creativityValue').textContent = agentData.creativity !== undefined ? agentData.creativity : 0.5;

    // Populate guardrail checkboxes
    const activeGuardrailTypes = agentData.guardrail_types || [];
    document.querySelectorAll('.guardrail-type-checkbox').forEach(cb => {
        cb.checked = activeGuardrailTypes.includes(cb.value);
    });

    const toggleGuardrailOptions = () => {
        const isEnabled = document.getElementById('guardrailsToggle').checked;
        const container = document.getElementById('guardrailOptionsContainer');
        if (container) {
            container.style.opacity = isEnabled ? '1' : '0.5';
            container.style.pointerEvents = isEnabled ? 'auto' : 'none';
        }
        document.querySelectorAll('.guardrail-type-checkbox').forEach(cb => {
            cb.disabled = !isEnabled;
        });
    };
    document.getElementById('guardrailsToggle').addEventListener('change', toggleGuardrailOptions);
    toggleGuardrailOptions();

    updateAgentAttachedToolsBox();

    // Sync system prompt between General and Prompts tab
    document.getElementById('personalityPromptInput').addEventListener('input', (e) => {
        document.getElementById('systemPromptConfigInput').value = e.target.value;
    });
    document.getElementById('systemPromptConfigInput').addEventListener('input', (e) => {
        document.getElementById('personalityPromptInput').value = e.target.value;
    });

    // Creativity slider label update
    document.getElementById('creativitySlider').addEventListener('input', (e) => {
        document.getElementById('creativityValue').textContent = e.target.value;
    });

    // Populate model dropdowns
    populateAgentModelDropdown();
    
    // Save button click
    document.getElementById('saveAgentBtn').replaceWith(document.getElementById('saveAgentBtn').cloneNode(true));
    document.getElementById('saveAgentBtn').addEventListener('click', async () => {
        const name = document.getElementById('agentNameInput').value;
        const agentDescInput = document.getElementById('agentDescInput');
        const description = agentDescInput ? agentDescInput.value : (agentData.description || 'Enterprise Agent');
        const system_prompt = document.getElementById('systemPromptConfigInput').value;
        const user_prompt = document.getElementById('userPromptConfigInput').value;
        const creativity = parseFloat(document.getElementById('creativitySlider').value);
        const guardrails = document.getElementById('guardrailsToggle').checked;
        const max_tool_calls = parseInt(document.getElementById('maxToolCallsInput').value) || 80;
        const guardrail_types = [...document.querySelectorAll('.guardrail-type-checkbox:checked')].map(cb => cb.value);
        
        // Handle model / llm_config_id selection
        const modelVal = document.getElementById('agentModelSelect').value;
        let llm_config_id = null;
        if (modelVal.startsWith('custom-')) {
            llm_config_id = parseInt(modelVal.replace('custom-', ''));
        }
        
        try {
            await authFetch(`/api/agents/${agentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, description, system_prompt, user_prompt,
                    creativity, guardrails, max_tool_calls, llm_config_id,
                    guardrail_types
                })
            });
            
            // Sync local agentData state
            agentData.name = name;
            agentData.description = description;
            agentData.system_prompt = system_prompt;
            agentData.user_prompt = user_prompt;
            agentData.creativity = creativity;
            agentData.guardrails = guardrails;
            agentData.max_tool_calls = max_tool_calls;
            agentData.llm_config_id = llm_config_id;
            agentData.guardrail_types = guardrail_types;
            
            document.getElementById('sidebarTitle').textContent = name;
            document.title = `${name} - Workspace`;
            
            // Sync settings select too
            document.getElementById('agentLlmSelect').value = llm_config_id || '';

            // Sync selected capabilities in the Integrations tab
            const intCheckboxes = document.querySelectorAll('input[name="agentIntTools"]');
            if (intCheckboxes.length > 0) {
                const selectedTools = [...document.querySelectorAll('input[name="agentIntTools"]:checked')].map(cb => cb.value);
                await authFetch(`/api/agents/${agentId}/tools`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ connected_tools: selectedTools })
                });
                agentData.connected_tools = selectedTools;
                const toolCount = selectedTools.length;
                const badge = document.getElementById('connectedToolsBadge');
                if (badge) badge.textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
            }
            
            alert('Agent configuration saved successfully!');
        } catch (e) {
            console.error('Error saving agent:', e);
            alert('Failed to save agent configuration.');
        }
    });

    // Bind Test Preview run
    document.getElementById('runTestBtn').addEventListener('click', async () => {
        const query = document.getElementById('testQueryInput').value;
        if (!query) {
            alert('Please enter a test query.');
            return;
        }
        
        const outputPanel = document.getElementById('testOutputPanel');
        const resolvedPrompt = document.getElementById('testResolvedPrompt');
        const agentReply = document.getElementById('testAgentReply');
        
        outputPanel.style.display = 'flex';
        resolvedPrompt.textContent = 'Resolving template...';
        agentReply.textContent = 'Executing agent message...';
        
        // Preview prompt resolution
        const userPromptTpl = document.getElementById('userPromptConfigInput').value;
        let resolved = query;
        if (userPromptTpl) {
            if (userPromptTpl.includes('{{query}}')) {
                resolved = userPromptTpl.replace('{{query}}', query);
            } else if (userPromptTpl.includes('{{prompt}}')) {
                resolved = userPromptTpl.replace('{{prompt}}', query);
            } else {
                resolved = `${userPromptTpl}\n\n${query}`;
            }
        }
        resolvedPrompt.textContent = resolved;
        
        // Simulate/Execute connection test
        try {
            if (activeThreadId === null) {
                await createNewThread("Test Connection Run");
            }
            const res = await authFetch(`/api/chat/threads/${activeThreadId}/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: query })
            });

            if (!res.ok) {
                throw new Error(`Server returned status ${res.status}`);
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let finalReply = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const eventData = JSON.parse(line);
                        if (eventData.type === 'stage') {
                            agentReply.textContent = `Stage: ${eventData.stage} ${eventData.tool ? '(' + eventData.tool + ')' : ''}`;
                        } else if (eventData.type === 'reply') {
                            finalReply = eventData.reply;
                        } else if (eventData.type === 'error') {
                            finalReply = `Error: ${eventData.message}`;
                        }
                    } catch (err) {
                        console.error("Stream parse error in test runner:", err);
                    }
                }
            }
            agentReply.textContent = finalReply || 'No response returned.';
        } catch (e) {
            agentReply.textContent = 'Error running agent test: ' + e.message;
        }
    });
}

function populateAgentModelDropdown() {
    const modelSelect = document.getElementById('agentModelSelect');
    if (!modelSelect) return;
    
    modelSelect.innerHTML = `
        <option value="gemini-2.0-flash">gemini-2.0-flash</option>
        <option value="gemini-2.5-pro">gemini-2.5-pro</option>
        <option value="gpt-4o">gpt-4o</option>
        <option value="gpt-4o-mini">gpt-4o-mini</option>
        <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet-20241022</option>
    `;
    
    // Add custom configs
    llmConfigs.forEach(conf => {
        const optionVal = `custom-${conf.id}`;
        modelSelect.innerHTML += `<option value="${optionVal}">${conf.provider.toUpperCase()} (${conf.model_name})</option>`;
    });
    
    // Select the current one
    if (agentData && agentData.llm_config_id) {
        modelSelect.value = `custom-${agentData.llm_config_id}`;
    } else if (agentData && agentData.model_name) {
        modelSelect.value = agentData.model_name;
    }
}

// Modify init to trigger config setup
const originalInit = init;
init = async function() {
    await originalInit();
    initAgentConfigForm();
};

// Boot
init();

// Split pane resizer logic
const resizeHandle = document.getElementById('resizeHandle');
const wsMain = document.querySelector('.ws-main');
const viewChat = document.getElementById('view-chat');

if (resizeHandle && wsMain && viewChat) {
    let isDragging = false;

    resizeHandle.addEventListener('mousedown', (e) => {
        isDragging = true;
        resizeHandle.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        const containerRect = wsMain.getBoundingClientRect();
        const relativeX = e.clientX - containerRect.left;

        const minWidth = 280;
        const maxWidth = containerRect.width - 280;
        let newChatWidth = Math.max(minWidth, Math.min(relativeX, maxWidth));
        
        const chatPercentage = (newChatWidth / containerRect.width) * 100;
        const configPercentage = 100 - chatPercentage;

        viewChat.style.width = `${chatPercentage}%`;
        
        document.querySelectorAll('.ws-view:not(#view-chat)').forEach(view => {
            view.style.width = `${configPercentage}%`;
        });
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            resizeHandle.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}
