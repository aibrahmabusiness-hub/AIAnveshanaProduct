// --- Custom Agent Dropdown Logic ---
function updateAgentDropdownSelection() {
    const triggerLabel = document.getElementById('chatAgentDropdownLabel');
    const menu = document.getElementById('chatAgentDropdownMenu');
    if (!triggerLabel || !menu) return;
    
    let activeVal = activeAgentId === null ? 'null' : activeAgentId.toString();
    let foundLabel = 'System Agent'; // fallback
    
    const options = menu.querySelectorAll('.dropdown-option');
    options.forEach(opt => {
        const check = opt.querySelector('.check-icon');
        if (opt.dataset.value === activeVal) {
            if (check) check.style.display = 'inline';
            foundLabel = opt.querySelector('span').textContent;
        } else {
            if (check) check.style.display = 'none';
        }
    });
    
    triggerLabel.textContent = foundLabel;
}

function setupAgentDropdown() {
    const trigger = document.getElementById('chatAgentDropdownTrigger');
    const menu = document.getElementById('chatAgentDropdownMenu');
    if (!trigger || !menu) return;

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isShowing = menu.style.display === 'flex';
        menu.style.display = isShowing ? 'none' : 'flex';
        const icon = document.getElementById('chatAgentDropdownIcon');
        if (icon) icon.style.transform = isShowing ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    menu.addEventListener('click', async (e) => {
        const opt = e.target.closest('.dropdown-option');
        if (opt) {
            const val = opt.dataset.value;
            activeAgentId = val === 'null' ? null : parseInt(val);
            updateAgentDropdownSelection();
            menu.style.display = 'none';
            const icon = document.getElementById('chatAgentDropdownIcon');
            if (icon) icon.style.transform = 'rotate(0deg)';
            
            await createNewThread();
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#chatAgentDropdown')) {
            menu.style.display = 'none';
            const icon = document.getElementById('chatAgentDropdownIcon');
            if (icon) icon.style.transform = 'rotate(0deg)';
        }
    });
    
    if (!document.getElementById('dropdown-option-hover-style')) {
        const style = document.createElement('style');
        style.id = 'dropdown-option-hover-style';
        style.innerHTML = '.dropdown-option:hover { background: #fff7ed !important; }';
        document.head.appendChild(style);
    }
}

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
const projectId = parseInt(pathParts[pathParts.length - 1]);
let projectData = null;
let activeAgentId = null;
let activeAgentData = null;
let llmConfigs = [];

// --- Init ---
async function init() {
    // Load User Profile dynamically to prevent mismatches
    try {
        const userRes = await authFetch('/api/auth/me');
        if (userRes.ok) {
            const userData = await userRes.json();
            if (userData.username) {
                localStorage.setItem('username', userData.username);
                const uAvatar = document.getElementById('userAvatar');
                if (uAvatar) uAvatar.textContent = userData.username.charAt(0).toUpperCase();
                const dUsername = document.getElementById('dropdownUsername');
                if (dUsername) dUsername.textContent = userData.username;
                const dAvatar = document.getElementById('dropdownAvatar');
                if (dAvatar) dAvatar.textContent = userData.username.charAt(0).toUpperCase();
                const dEmail = document.querySelector('.profile-email');
                if (dEmail && userData.email) dEmail.textContent = userData.email;
            }
        }
    } catch (e) {
        console.error("Failed to load user profile", e);
    }

    // Load project info
    const res = await authFetch(`/api/projects/${projectId}`);
    if (!res.ok) {
        alert("Project not found or you don't have access.");
        window.location.href = '/';
        return;
    }
    const data = await res.json();
    projectData = data.project;
    document.getElementById('sidebarTitle').textContent = projectData.name;
    document.title = `${projectData.name} - Workspace`;

    // Load LLM configurations globally so Agent dropdowns have them
    try {
        const llmRes = await authFetch('/api/settings/llm');
        const llmData = await llmRes.json();
        llmConfigs = llmData.configs || [];
        populateAgentModelDropdown();
    } catch (err) {
        console.error("Failed to load global LLM configs", err);
    }

    // Load agents grid
    await loadProjectAgentsList();

    // Load other views only when clicked, except chat history
    loadChatThreads();
}

// --- Sidebar Navigation ---
document.querySelectorAll('.ws-nav-item[data-view]').forEach(item => {
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
});

// --- Chat & Threads ---
const promptInput = document.getElementById('promptInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const newThreadBtn = document.getElementById('newThreadBtn');

let activeThreadId = null;

// New Thread Button
if (newThreadBtn) {
    newThreadBtn.addEventListener('click', async () => {
        await createNewThread();
    });
}

async function createNewThread(initialPrompt = null) {
    const title = initialPrompt ? (initialPrompt.substring(0, 30) + (initialPrompt.length > 30 ? '...' : '')) : `Chat Session ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    try {
        const res = await authFetch('/api/chat/threads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId, agent_id: activeAgentId || null, title })
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
        const res = await authFetch(`/api/chat/threads?project_id=${projectId}`);
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
            <div class="history-item ${t.id === activeThreadId ? 'active' : ''}" data-thread-id="${t.id}" data-agent-id="${t.agent_id === null ? 'null' : t.agent_id}" style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-radius:6px; cursor:pointer;">
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
            
            // Update agent select dropdown
            const threadAgentId = item.dataset.agentId;
            activeAgentId = threadAgentId === 'null' ? null : parseInt(threadAgentId);
            if (typeof updateAgentDropdownSelection === 'function') {
                updateAgentDropdownSelection();
            }
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

if (sendBtn) sendBtn.addEventListener('click', sendMessage);
if (promptInput) promptInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

// --- Tools View ---
async function loadToolsView() {
    const toolsList = document.getElementById('agentToolsGrid');
    if (toolsList) {
        toolsList.style.display = 'block';
        await renderIntegrationsList('agentToolsGrid', false);
    }
}

// --- Knowledge Base ---
async function loadKnowledgeBase() {
    const res = await authFetch(`/api/knowledge/${activeAgentId}`);
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
document.getElementById('kbFileInput')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    
    await authFetch(`/api/knowledge/${activeAgentId}`, {
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
        const selected = (activeAgentData ? activeAgentData.llm_config_id : null) === conf.id ? 'selected' : '';
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
document.getElementById('saveAgentLlmBtn')?.addEventListener('click', async () => {
    const configId = document.getElementById('agentLlmSelect').value;
    const llm_config_id = configId ? parseInt(configId) : null;
    await authFetch(`/api/agents/${activeAgentId}/llm`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_config_id })
    });
    if (activeAgentData) activeAgentData.llm_config_id = llm_config_id;
    // Sync agent model dropdown too
    populateAgentModelDropdown();
    alert('Agent LLM updated!');
});

// Add new LLM Configuration
document.getElementById('addLlmConfigForm')?.addEventListener('submit', async (e) => {
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
document.getElementById('testLlmConnBtn')?.addEventListener('click', async () => {
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
document.getElementById('saveSfCreds')?.addEventListener('click', async () => {
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

document.getElementById('testSfCredsBtn')?.addEventListener('click', async () => {
    const creds = {
        instance_url: document.getElementById('sfUrl').value,
        username: document.getElementById('sfUser').value,
        password: document.getElementById('sfPass').value,
        security_token: document.getElementById('sfToken').value,
    };
    await testCredentials('salesforce', creds, 'sfTestStatus');
});

// ServiceNow credentials
document.getElementById('saveSnCreds')?.addEventListener('click', async () => {
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

document.getElementById('testSnCredsBtn')?.addEventListener('click', async () => {
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
document.getElementById('saveGmCreds')?.addEventListener('click', async () => {
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

document.getElementById('testGmCredsBtn')?.addEventListener('click', async () => {
    const creds = {
        username: document.getElementById('gmUser').value,
        password: document.getElementById('gmToken').value,
        configured: true
    };
    await testCredentials('gmail', creds, 'gmTestStatus');
});

// Jira credentials
document.getElementById('saveJrCreds')?.addEventListener('click', async () => {
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

document.getElementById('testJrCredsBtn')?.addEventListener('click', async () => {
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

document.getElementById('createNewWorkflowBtn')?.addEventListener('click', () => {
    if (workflowStepsList) {
        workflowStepsList.innerHTML = '';
        if (typeof addStepRow === 'function') addStepRow(); // Start with one empty step
    }
    const frame = document.getElementById('react-flow-frame');
    if (frame) {
        const agId = activeAgentId || 'null';
        frame.src = `/v2-canvas?id=new_workflow&agent_id=${agId}&project_id=${projectId}`;
    }
    if (workflowModal) workflowModal.classList.add('active');
});

if (closeWorkflowModalBtn && workflowModal) {
    closeWorkflowModalBtn.addEventListener('click', () => workflowModal.classList.remove('active'));
}
if (cancelWorkflowModalBtn && workflowModal) {
    cancelWorkflowModalBtn.addEventListener('click', () => workflowModal.classList.remove('active'));
}

window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'close-v2-editor') {
        const workflowModal = document.getElementById('workflowModal');
        if (workflowModal) workflowModal.classList.remove('active');
    }
});


const INTEGRATION_GROUPS = [
    {
        id: 'outlook',
        name: 'Microsoft Outlook',
        desc: 'Calendar scheduling and email reading',
        tools: ['outlook_calendar', 'outlook_email'],
        logo: 'https://upload.wikimedia.org/wikipedia/commons/d/df/Microsoft_Office_Outlook_%282018%E2%80%93present%29.svg'
    },
    {
        id: 'servicenow',
        name: 'ServiceNow',
        desc: 'Incident creation & database table queries',
        tools: ['servicenow_incidents', 'servicenow_tables'],
        logo: 'https://upload.wikimedia.org/wikipedia/commons/5/57/ServiceNow_logo.svg'
    },
    {
        id: 'salesforce',
        name: 'Salesforce CRM',
        desc: 'CRM record queries & lead/account creation',
        tools: ['salesforce_query', 'salesforce_create'],
        logo: 'https://cdn.worldvectorlogo.com/logos/salesforce-2.svg'
    },
    {
        id: 'gmail',
        name: 'Gmail Suite',
        desc: 'Standard email reading & communications sending',
        tools: ['gmail_read', 'gmail_send'],
        logo: 'https://cdn.worldvectorlogo.com/logos/gmail-icon.svg'
    },
    {
        id: 'jira',
        name: 'Atlassian Jira',
        desc: 'Issue creation, search queries, and comments tracking',
        tools: ['jira_issues'],
        logo: 'https://cdn.worldvectorlogo.com/logos/jira-1.svg'
    },
    {
        id: 'google_search_tool',
        name: 'Google Web Search',
        desc: 'Search the live web keylessly for real-time information and facts',
        tools: ['google_search'],
        systemDefault: true,
        logo: 'https://cdn.worldvectorlogo.com/logos/google-icon-1.svg'
    }
];


let currentAccountsModalToolId = null;

async function showConnectionAccountsModal(toolId) {
    currentAccountsModalToolId = toolId;
    const modal = document.getElementById('connectionAccountsModal');
    if (!modal) {
        alert("Connection modal not found in HTML!");
        return;
    }
    console.log("Accessing INTEGRATION_GROUPS at showConnectionAccountsModal", new Error().stack);
    const groupName = INTEGRATION_GROUPS.find(g => g.id === toolId)?.name || toolId;
    const titleEl = document.getElementById('connModalTitle');
    if (titleEl) titleEl.textContent = `Manage ${groupName} Accounts`;
    
    hideConnAccountForm();
    await refreshConnAccountsList();
    
    modal.classList.add('active'); 
    modal.style.display = 'flex';
}

window.closeConnectionAccountsModal = function() {
    const modal = document.getElementById('connectionAccountsModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
    hideConnAccountForm();
}

async function refreshConnAccountsList() {
    const listEl = document.getElementById('connAccountsList');
    if (!listEl) return;
    listEl.innerHTML = '<div style="padding:10px; color:#64748b; font-size:0.85rem;">Loading accounts...</div>';
    try {
        const res = await authFetch(`/api/credentials/${currentAccountsModalToolId}/accounts`);
        const data = await res.json();
        const accounts = data.connections || [];
        
        if (!accounts || accounts.length === 0) {
            listEl.innerHTML = '<div style="padding:10px; color:#64748b; font-size:0.85rem;">No accounts connected.</div>';
            return;
        }
        
        listEl.innerHTML = accounts.map(acc => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;">
                <div>
                    <div style="font-weight:600; font-size:0.9rem; color:#0f172a;">${acc.name || 'Unnamed Account'}</div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn-cancel" onclick="editConnAccount('${acc.id}')" style="padding:4px 8px; font-size:0.75rem;">Edit</button>
                    <button class="btn-cancel" onclick="deleteConnAccount('${acc.id}')" style="padding:4px 8px; font-size:0.75rem; color:#ef4444; border-color:#fca5a5;">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        listEl.innerHTML = '<div style="padding:10px; color:#ef4444; font-size:0.85rem;">Failed to load accounts.</div>';
    }
}

window.deleteConnAccount = async function(id) {
    if (!confirm("Are you sure you want to delete this account?")) return;
    await authFetch(`/api/credentials/${currentAccountsModalToolId}/accounts/${id}`, { method: 'DELETE' });
    await refreshConnAccountsList();
    
    if (document.getElementById('view-agents') && document.getElementById('view-agents').classList.contains('active')) {
        loadAgentIntegrationsView();
    } else {
        loadToolsView();
    }
}

window.showAddConnAccountForm = function(accountId = null) {
    document.getElementById('connAccountFormContainer').style.display = 'block';
    document.getElementById('connFormTitle').textContent = accountId ? 'Edit Account' : '+ Add Account';
    document.getElementById('connFormAccountId').value = accountId || '';
    document.getElementById('connFormAccountName').value = '';
    document.getElementById('connTestStatus').style.display = 'none';
    
    const sourcePanel = document.getElementById(`settings-panel-${currentAccountsModalToolId}`);
    const originalParent = document.getElementById('settingsFormsContainer');
    if (sourcePanel && originalParent && sourcePanel.parentNode !== originalParent) {
        originalParent.appendChild(sourcePanel);
    }
    
    const dynamicFields = document.getElementById('connDynamicFields');
    dynamicFields.innerHTML = '';
    
    if (sourcePanel) {
        dynamicFields.appendChild(sourcePanel);
        sourcePanel.classList.add('active');
        sourcePanel.style.display = 'block';
        
        // Hide native buttons from the source panel
        const saveBtns = sourcePanel.querySelectorAll('.btn-primary, .btn-cancel, #testSfCredsBtn, #saveSfCreds, #testSnCredsBtn, #saveSnCreds, #testGmCredsBtn, #saveGmCreds, #testJrCredsBtn, #saveJrCreds');
        saveBtns.forEach(btn => btn.style.display = 'none');
        
        if (!accountId) {
            sourcePanel.querySelectorAll('input').forEach(input => input.value = '');
        }
    }
}

window.hideConnAccountForm = function() {
    const container = document.getElementById('connAccountFormContainer');
    if (container) container.style.display = 'none';
    
    const sourcePanel = document.getElementById(`settings-panel-${currentAccountsModalToolId}`);
    const originalParent = document.getElementById('settingsFormsContainer');
    
    if (sourcePanel && originalParent) {
        const saveBtns = sourcePanel.querySelectorAll('.btn-primary, .btn-cancel, #testSfCredsBtn, #saveSfCreds, #testSnCredsBtn, #saveSnCreds, #testGmCredsBtn, #saveGmCreds, #testJrCredsBtn, #saveJrCreds');
        saveBtns.forEach(btn => btn.style.display = '');
        
        sourcePanel.style.display = 'none';
        originalParent.appendChild(sourcePanel);
    }
}

window.editConnAccount = async function(id) {
    window.showAddConnAccountForm(id);
    
    try {
        const res = await authFetch(`/api/credentials/${currentAccountsModalToolId}/accounts`);
        const accounts = await res.json();
        const account = accounts.find(a => String(a.id) === String(id));
        
        if (account) {
            document.getElementById('connFormAccountName').value = account.name;
            const creds = account.credentials || {};
            
            if (currentAccountsModalToolId === 'salesforce') {
                document.getElementById('sfUrl').value = creds.instance_url || '';
                document.getElementById('sfUser').value = creds.username || '';
                document.getElementById('sfPass').value = creds.password || '';
                document.getElementById('sfToken').value = creds.security_token || '';
            } else if (currentAccountsModalToolId === 'servicenow') {
                document.getElementById('snUrl').value = creds.instance_url || '';
                document.getElementById('snClientId').value = creds.client_id || '';
                document.getElementById('snClientSecret').value = creds.client_secret || '';
                document.getElementById('snUser').value = creds.username || '';
                document.getElementById('snPass').value = creds.password || '';
            } else if (currentAccountsModalToolId === 'gmail') {
                document.getElementById('gmUser').value = creds.username || '';
                document.getElementById('gmToken').value = creds.password || '';
            } else if (currentAccountsModalToolId === 'jira') {
                document.getElementById('jrUrl').value = creds.instance_url || '';
                document.getElementById('jrUser').value = creds.username || '';
                document.getElementById('jrToken').value = creds.password || '';
            }
        }
    } catch (err) {
        console.error("Failed to load account details", err);
    }
}

function getCredsFromForm() {
    let creds = {};
    if (currentAccountsModalToolId === 'salesforce') {
        creds = {
            instance_url: document.getElementById('sfUrl').value,
            username: document.getElementById('sfUser').value,
            password: document.getElementById('sfPass').value,
            security_token: document.getElementById('sfToken').value,
        };
    } else if (currentAccountsModalToolId === 'servicenow') {
        creds = {
            instance_url: document.getElementById('snUrl').value,
            client_id: document.getElementById('snClientId').value,
            client_secret: document.getElementById('snClientSecret').value,
            username: document.getElementById('snUser').value,
            password: document.getElementById('snPass').value,
        };
    } else if (currentAccountsModalToolId === 'gmail') {
        creds = {
            username: document.getElementById('gmUser').value,
            password: document.getElementById('gmToken').value,
            configured: true
        };
    } else if (currentAccountsModalToolId === 'jira') {
        creds = {
            instance_url: document.getElementById('jrUrl').value,
            username: document.getElementById('jrUser').value,
            password: document.getElementById('jrToken').value,
        };
    }
    return creds;
}

window.saveConnAccount = async function() {
    const name = document.getElementById('connFormAccountName').value.trim() || 'Unnamed Account';
    const accountId = document.getElementById('connFormAccountId').value;
    const creds = getCredsFromForm();
    
    const payload = {
        name: name,
        credentials: creds
    };
    if (accountId) payload.id = parseInt(accountId);
    
    try {
        await authFetch(`/api/credentials/${currentAccountsModalToolId}/accounts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        hideConnAccountForm();
        await refreshConnAccountsList();
        
        if (document.getElementById('view-agents') && document.getElementById('view-agents').classList.contains('active')) {
            loadAgentIntegrationsView();
        } else {
            loadToolsView();
        }
    } catch (err) {
        console.error("Failed to save account", err);
        alert("Failed to save account.");
    }
}

window.testConnAccount = async function() {
    const creds = getCredsFromForm();
    const statusDiv = document.getElementById('connTestStatus');
    statusDiv.style.display = 'inline-block';
    statusDiv.textContent = 'Testing...';
    statusDiv.style.color = '#64748b';
    
    try {
        const res = await authFetch('/api/credentials/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tool_name: currentAccountsModalToolId, credentials: creds })
        });
        const data = await res.json();
        if (data.status === 'success') {
            statusDiv.textContent = 'Success!';
            statusDiv.style.color = '#10b981';
        } else {
            statusDiv.textContent = 'Failed';
            statusDiv.style.color = '#ef4444';
        }
    } catch (err) {
        statusDiv.textContent = 'Error';
        statusDiv.style.color = '#ef4444';
    }
}




async function renderIntegrationsList(containerId, isAgentContext) {
    const listContainer = document.getElementById(containerId);
    if (!listContainer) return;
    
    const res = await authFetch('/api/tools');
    const data = await res.json();
    const connected = activeAgentData ? (activeAgentData.connected_tools || []) : [];
    
    const statuses = {};
    console.log("Accessing INTEGRATION_GROUPS at renderIntegrationsList", new Error().stack);
    for (const group of INTEGRATION_GROUPS) {
        if (group.systemDefault) {
            statuses[group.id] = 'system';
            continue;
        }
        try {
            const accRes = await authFetch(`/api/credentials/${group.id}/accounts`);
            const data = await accRes.json();
            const accs = data.connections || [];
            statuses[group.id] = Array.isArray(accs) ? accs.length : 0;
        } catch (err) {
            statuses[group.id] = 0;
        }
    }
    
    listContainer.innerHTML = INTEGRATION_GROUPS.map(group => {
        const numAccounts = statuses[group.id];
        let isConnected = false;
        let badgeText = 'Not Configured';
        
        if (numAccounts === 'system') {
            isConnected = true;
            badgeText = 'System Default';
        } else if (numAccounts > 0) {
            isConnected = true;
            badgeText = `${numAccounts} Account${numAccounts !== 1 ? 's' : ''} Connected`;
        }
        
        const badgeClass = isConnected ? 'agent-integration-badge connected' : 'agent-integration-badge unconfigured';
        
        const groupTools = data.tools.filter(t => group.tools.includes(t.id));
        
        return `
            <div class="agent-integration-item" id="agent-int-item-${containerId}-${group.id}">
                <div class="agent-integration-summary">
                    <div style="display:flex; align-items:center; gap:16px;">
                        <img src="${group.logo}" alt="${group.name} logo" style="width:32px; height:32px; object-fit:contain;" />
                        <div class="agent-integration-title">
                            <strong>${group.name}</strong>
                            <span>${group.desc}</span>
                        </div>
                    </div>
                    <div class="agent-integration-actions">
                        <span class="${badgeClass}">${badgeText}</span>
                        ${!group.systemDefault ? `
                            <button type="button" class="agent-connect-link" data-tool-target="${group.id}">${isConnected ? 'Manage' : 'Connect'}</button>
                        ` : ''}
                        ${isConnected ? `
                            <svg class="agent-expand-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        ` : ''}
                    </div>
                </div>
                <div class="agent-integration-details">
                    ${isAgentContext ? `
                    <div style="font-size:0.85rem; font-weight:600; color:var(--text-main); margin-bottom:10px;">Enable Capabilities for this Agent:</div>
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        ${groupTools.map(tool => {
                            const isChecked = connected.includes(tool.id) ? 'checked' : '';
                            return `
                                <label style="display:flex; align-items:flex-start; gap:10px; cursor:pointer;">
                                    <input type="checkbox" name="agentIntTools-${containerId}" value="${tool.id}" ${isChecked} style="margin-top:3px; accent-color:var(--orange-primary);">
                                    <div>
                                        <div style="font-size:0.85rem; font-weight:600; color:var(--text-main);">${tool.name}</div>
                                        <div style="font-size:0.75rem; color:var(--text-muted);">${tool.description}</div>
                                    </div>
                                </label>
                            `;
                        }).join('')}
                    </div>
                    ` : `
                    <div style="font-size:0.85rem; font-weight:600; color:var(--text-main); margin-bottom:10px;">Capabilities Available:</div>
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        ${groupTools.map(tool => `
                            <div style="display:flex; align-items:flex-start; gap:10px;">
                                <div style="margin-top:4px; width:6px; height:6px; border-radius:50%; background:var(--primary-color);"></div>
                                <div>
                                    <div style="font-size:0.85rem; font-weight:600; color:var(--text-main);">${tool.name}</div>
                                    <div style="font-size:0.75rem; color:var(--text-muted);">${tool.description}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    `}
                </div>
            </div>
        `;
    }).join('');
    
    INTEGRATION_GROUPS.forEach(group => {
        const itemEl = document.getElementById(`agent-int-item-${containerId}-${group.id}`);
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
                showConnectionAccountsModal(group.id);
            });
        }
    });
    
    if (isAgentContext) {
        document.querySelectorAll(`input[name="agentIntTools-${containerId}"]`).forEach(cb => {
            cb.addEventListener('change', async () => {
                const selectedTools = [...document.querySelectorAll(`input[name="agentIntTools-${containerId}"]:checked`)].map(c => c.value);
                await authFetch(`/api/agents/${agentId}/tools`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ connected_tools: selectedTools })
                });
                if (activeAgentData) {
                    activeAgentData.connected_tools = selectedTools;
                }
                const toolCount = selectedTools.length;
                const badge = document.getElementById('connectedToolsBadge');
                if (badge) badge.textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
                if (typeof updateAgentAttachedToolsBox === 'function') updateAgentAttachedToolsBox();
            });
        });
    }
}


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

if (addStepBtn) addStepBtn.addEventListener('click', addStepRow);

function reorderSteps() {
    [...workflowStepsList.children].forEach((div, idx) => {
        div.querySelector('strong').textContent = `Step ${idx + 1}`;
    });
}

// Save Workflow
if (createWorkflowForm) {
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
}

// Load Workflows
async function loadWorkflowsView() {
    const res = await authFetch(`/api/workflows?project_id=${projectId}&agent_id=${activeAgentId || ''}`);
    const data = await res.json();
    const workflowsList = document.getElementById('workflowsList');

    if (!data.workflows || data.workflows.length === 0) {
        workflowsList.innerHTML = '<p style="color:var(--text-muted); font-size:0.85rem;">No workflows configured for this agent yet.</p>';
        return;
    }

    workflowsList.innerHTML = data.workflows.map(wf => {
        let stepCount = 0;
        let stepNames = 'Canvas Flow';
        if (Array.isArray(wf.steps)) {
            stepCount = wf.steps.length;
            stepNames = wf.steps.map(s => s.tool || s.type).join(' ➔ ');
        } else if (wf.steps && wf.steps.nodes) {
            stepCount = wf.steps.nodes.length;
        }
        return `
        <div style="border:1px solid var(--border-color); border-radius:12px; padding:20px; display:flex; justify-content:space-between; align-items:center; background:white; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div>
                <strong style="font-size:1rem; color:var(--text-main);">${wf.name}</strong>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">${stepCount} step${stepCount !== 1 ? 's' : ''}: ${stepNames}</div>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="openEditWorkflow(${wf.id}, ${wf.agent_id})" style="padding:6px 12px; font-size:0.8rem; background: #64748b;">Edit</button>
                <button class="btn-primary" onclick="openExecWorkflow(${wf.id})" style="padding:6px 12px; font-size:0.8rem;">Run</button>
                <button class="btn-cancel" onclick="deleteWorkflow(${wf.id})" style="padding:6px 12px; font-size:0.8rem; border:1px solid #ef4444; color:#ef4444; background:none;">Delete</button>
            </div>
        </div>
        `;
    }).join('');
}

window.openEditWorkflow = function(wfId, agentId) {
    const frame = document.getElementById('react-flow-frame');
    if (frame) {
        const agId = agentId || activeAgentId || 'null';
        frame.src = `/v2-canvas?id=${wfId}&agent_id=${agId}&project_id=${projectId}`;
    }
    const workflowModal = document.getElementById('workflowModal');
    if (workflowModal) workflowModal.classList.add('active');
};


async function deleteWorkflow(wfId) {
    if (confirm('Delete this workflow?')) {
        await authFetch(`/api/workflows/${wfId}`, { method: 'DELETE' });
        await loadWorkflowsView();
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

document.getElementById('closeExecModalBtn')?.addEventListener('click', () => execModal.classList.remove('active'));
document.getElementById('cancelExecModalBtn')?.addEventListener('click', () => execModal.classList.remove('active'));

if(executeWorkflowForm) {
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
}

async function loadAgentIntegrationsView() {
    await renderIntegrationsList('agentIntegrationsList', true);
}

async function updateAgentAttachedToolsBox() {
    const attachedBox = document.getElementById('agentAttachedTools');
    if (!attachedBox) return;

    try {
        const [toolsRes, credsRes] = await Promise.all([
            authFetch('/api/tools'),
            authFetch('/api/credentials')
        ]);
        
        const data = await toolsRes.json();
        const credsData = await credsRes.json();
        
        // Map available connections per tool
        const availableConnections = {};
        if (credsData.success && credsData.credentials) {
            credsData.credentials.forEach(cred => {
                if (cred.credentials && cred.credentials.connections && cred.credentials.connections.length > 0) {
                    availableConnections[cred.tool_name.toLowerCase()] = cred.credentials.connections;
                } else if (cred.credentials && Object.keys(cred.credentials).length > 0) {
                    // Legacy format
                    availableConnections[cred.tool_name.toLowerCase()] = [
                        { id: 'default', name: cred.credentials.username || cred.credentials.instance_url || 'Default Connection' }
                    ];
                }
            });
        }

        const connected = activeAgentData.connected_tools || [];

        let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
        
        // Knowledge Base option
        html += `
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer; padding: 10px; background:white; border-radius:8px; border:1px solid var(--border-color);">
                <input type="checkbox" id="kbOptionCheckbox" style="accent-color: var(--orange-primary); width: 16px; height: 16px; flex-shrink:0;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                    <div style="font-size:0.9rem; font-weight:600; color:var(--text-color);">Knowledge Base (Vector RAG)</div>
                </div>
            </label>
        `;

        if (data.tools && data.tools.length > 0) {
            const groupedTools = {};
            const otherTools = [];

            INTEGRATION_GROUPS.forEach(g => {
                // Fix Microsoft Outlook logo
                if (g.id === 'outlook_email' || g.id === 'outlook_calendar' || g.name.includes('Outlook')) {
                    g.logo = 'https://cdn.worldvectorlogo.com/logos/microsoft-outlook-1.svg';
                }
                const needsConnection = g.id !== 'google_search_tool';
                if (!needsConnection || availableConnections[g.id]) {
                    groupedTools[g.id] = { group: g, tools: [], connections: availableConnections[g.id] || [] };
                }
            });

            data.tools.forEach(t => {
                const group = INTEGRATION_GROUPS.find(g => (g.tools && g.tools.includes(t.id)) || t.id.startsWith(g.id) || (g.id === 'google_search_tool' && t.id === 'google_search'));
                if (group) {
                    if (groupedTools[group.id]) {
                        groupedTools[group.id].tools.push(t);
                    }
                } else {
                    otherTools.push(t);
                }
            });

            // Render groups
            Object.values(groupedTools).forEach(item => {
                if (item.tools.length === 0) return;
                const groupId = 'agent-group-' + item.group.id;
                
                const getToolSelection = (toolId) => {
                    const match = connected.find(ct => ct === toolId || ct.startsWith(toolId + ':'));
                    if (match) {
                        const parts = match.split(':');
                        return { active: true, connId: parts.length > 1 ? parts[1] : null };
                    }
                    return { active: false, connId: null };
                };
                
                const anyChecked = item.tools.some(t => getToolSelection(t.id).active);
                
                html += `
                    <div style="border:1px solid var(--border-color); border-radius:8px; overflow:hidden; background:white;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:10px; cursor:pointer; background:#f8fafc;" onclick="document.getElementById('${groupId}').style.display = document.getElementById('${groupId}').style.display === 'none' ? 'block' : 'none'">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <img src="${item.group.logo}" style="width:20px; height:20px; object-fit:contain;">
                                <div style="font-size:0.85rem; font-weight:600; color:var(--text-color);">${item.group.name}</div>
                            </div>
                            <div style="font-size:0.75rem; color:var(--text-muted);">
                                ${anyChecked ? '<span style="color:var(--orange-primary); font-weight:bold;">Active</span> • ' : ''}
                                Click to expand
                            </div>
                        </div>
                        <div id="${groupId}" style="display:${anyChecked ? 'block' : 'none'}; border-top:1px solid var(--border-color); padding:8px 10px; background:white;">
                            ${item.tools.map(t => {
                                const sel = getToolSelection(t.id);
                                const isChecked = sel.active ? 'checked' : '';
                                
                                let selectHtml = '';
                                if (item.connections.length > 0) {
                                    selectHtml = '<select class="tool-connection-select" data-tool="' + t.id + '" style="margin-left:auto; font-size:0.75rem; padding:2px 4px; border-radius:4px; border:1px solid var(--border-color); background:white;">' +
                                        item.connections.map(c => '<option value="' + c.id + '" ' + (sel.connId === c.id ? 'selected' : '') + '>' + (c.name || c.id) + '</option>').join('') +
                                        '</select>';
                                }

                                return `
                                    <label style="display:flex; align-items:center; gap:8px; cursor:pointer; padding: 6px 4px;">
                                        <input type="checkbox" class="tool-selection-checkbox" value="${t.id}" ${isChecked} style="accent-color: var(--orange-primary); width: 14px; height: 14px; flex-shrink:0;">
                                        <div style="font-size:0.8rem; color:var(--text-color);">${t.name}</div>
                                        ${selectHtml}
                                    </label>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });

            // Render Other Capabilities
            if (otherTools.length > 0) {
                const getOtherSelection = (toolId) => {
                    return connected.some(ct => ct === toolId || ct.startsWith(toolId + ':'));
                };
                const anyChecked = otherTools.some(t => getOtherSelection(t.id));
                
                html += `
                    <div style="border:1px solid var(--border-color); border-radius:8px; overflow:hidden; background:white;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:10px; cursor:pointer; background:#f8fafc;" onclick="document.getElementById('agent-group-others').style.display = document.getElementById('agent-group-others').style.display === 'none' ? 'block' : 'none'">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:#64748b;"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>
                                <div style="font-size:0.85rem; font-weight:600; color:var(--text-color);">Other Capabilities</div>
                            </div>
                            <div style="font-size:0.75rem; color:var(--text-muted);">
                                ${anyChecked ? '<span style="color:var(--orange-primary); font-weight:bold;">Active</span> • ' : ''}
                                Click to expand
                            </div>
                        </div>
                        <div id="agent-group-others" style="display:${anyChecked ? 'block' : 'none'}; border-top:1px solid var(--border-color); padding:8px 10px; background:white;">
                            ${otherTools.map(t => {
                                const isChecked = getOtherSelection(t.id) ? 'checked' : '';
                                return `
                                    <label style="display:flex; align-items:center; gap:8px; cursor:pointer; padding: 6px 4px;">
                                        <input type="checkbox" class="tool-selection-checkbox" value="${t.id}" ${isChecked} style="accent-color: var(--orange-primary); width: 14px; height: 14px; flex-shrink:0;">
                                        <div style="font-size:0.8rem; color:var(--text-color);">${t.name}</div>
                                    </label>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            }
        }

        html += '</div>';
        attachedBox.innerHTML = html;
        
        const kbCheckbox = document.getElementById('kbOptionCheckbox');
        if (kbCheckbox) {
            kbCheckbox.addEventListener('change', (e) => {
                if(e.target.checked) {
                    if(confirm("Manage Knowledge Base documents now?")) {
                        const kbNavItem = document.querySelector('.ws-nav-item[data-view="knowledge"]');
                        if (kbNavItem) kbNavItem.click();
                    }
                }
            });
        }

    } catch (e) {
        console.error("Error loading tools:", e);
        attachedBox.innerHTML = '<div style="color:red;">Error loading tools.</div>';
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
        const showSaveBtn = (viewId === 'agents' && activeAgentId !== null);
        document.getElementById('saveAgentBtn').style.display = showSaveBtn ? 'block' : 'none';
        
        if (viewId === 'agents' && activeAgentId) {
             document.getElementById('agents-list-screen').style.display = 'none';
             document.getElementById('agent-config-screen').style.display = 'flex';
        } else if (viewId === 'agents') {
             document.getElementById('agent-config-screen').style.display = 'none';
             document.getElementById('agents-list-screen').style.display = 'block';
        }
    });
});
    // Trigger display check on init
    const activeMainView = document.querySelector('.ws-nav-item.active').dataset.view;
    document.getElementById('saveAgentBtn').style.display = (activeMainView === 'agents' && activeAgentId !== null) ? 'block' : 'none';

    // 2. Populate form fields if agent is selected
    document.getElementById('agentNameInput').value = activeAgentData?.name || '';
    const agentDescInput = document.getElementById('agentDescInput');
    if (agentDescInput) agentDescInput.value = activeAgentData?.description || '';
    document.getElementById('personalityPromptInput').value = activeAgentData?.system_prompt || '';
    document.getElementById('systemPromptConfigInput').value = activeAgentData?.system_prompt || '';
    document.getElementById('userPromptConfigInput').value = activeAgentData?.user_prompt || '';
    document.getElementById('maxToolCallsInput').value = activeAgentData?.max_tool_calls || 80;
    document.getElementById('guardrailsToggle').checked = activeAgentData ? activeAgentData.guardrails !== false : true;
    document.getElementById('creativitySlider').value = activeAgentData?.creativity !== undefined ? activeAgentData.creativity : 0.5;
    document.getElementById('creativityValue').textContent = activeAgentData?.creativity !== undefined ? activeAgentData.creativity : 0.5;

    // Populate guardrail checkboxes
    const activeGuardrailTypes = activeAgentData?.guardrail_types || [];
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
    document.getElementById('guardrailsToggle')?.addEventListener('change', toggleGuardrailOptions);
    toggleGuardrailOptions();

    updateAgentAttachedToolsBox();

    // Sync system prompt between General and Prompts tab
    document.getElementById('personalityPromptInput')?.addEventListener('input', (e) => {
        document.getElementById('systemPromptConfigInput').value = e.target.value;
    });
    document.getElementById('systemPromptConfigInput')?.addEventListener('input', (e) => {
        document.getElementById('personalityPromptInput').value = e.target.value;
    });

    // Creativity slider label update
    document.getElementById('creativitySlider')?.addEventListener('input', (e) => {
        document.getElementById('creativityValue').textContent = e.target.value;
    });

    // Populate model dropdowns
    populateAgentModelDropdown();
    
    // Save button click - exposed globally
    window.saveAgentConfig = async () => {
        try {
        const name = document.getElementById('agentNameInput').value;
        const agentDescInput = document.getElementById('agentDescInput');
        const description = agentDescInput ? agentDescInput.value : (activeAgentData.description || 'Enterprise Agent');
        const system_prompt = document.getElementById('systemPromptConfigInput').value;
        const user_prompt = document.getElementById('userPromptConfigInput').value;
        const creativity = parseFloat(document.getElementById('creativitySlider').value);
        const guardrails = document.getElementById('guardrailsToggle').checked;
        const max_tool_calls = parseInt(document.getElementById('maxToolCallsInput').value) || 80;
        const guardrail_types = [...document.querySelectorAll('.guardrail-type-checkbox:checked')].map(cb => cb.value);
        const selected_tools = [...document.querySelectorAll('.tool-selection-checkbox:checked')].map(cb => {
            let val = cb.value;
            const select = document.querySelector(`.tool-connection-select[data-tool="${val}"]`);
            if (select && select.value) {
                val = val + ':' + select.value;
            }
            return val;
        });
        
        // Handle model / llm_config_id selection
        const modelVal = document.getElementById('agentModelSelect').value;
        let llm_config_id = null;
        if (modelVal.startsWith('custom-')) {
            llm_config_id = parseInt(modelVal.replace('custom-', ''));
        }
        

            await authFetch(`/api/agents/${activeAgentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, description, system_prompt, user_prompt,
                    creativity, guardrails, max_tool_calls, llm_config_id,
                    guardrail_types
                })
            });
            
            // Save tools
            await authFetch(`/api/agents/${activeAgentId}/tools`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ connected_tools: selected_tools })
            });

            // Sync local activeAgentData state
            activeAgentData.name = name;
            activeAgentData.description = description;
            activeAgentData.system_prompt = system_prompt;
            activeAgentData.user_prompt = user_prompt;
            activeAgentData.creativity = creativity;
            activeAgentData.guardrails = guardrails;
            activeAgentData.max_tool_calls = max_tool_calls;
            if (activeAgentData) activeAgentData.llm_config_id = llm_config_id;
            activeAgentData.guardrail_types = guardrail_types;
            
            document.getElementById('sidebarTitle').textContent = name;
            document.title = `${name} - Workspace`;
            
            // Sync settings select too
            document.getElementById('agentLlmSelect').value = llm_config_id || '';

            // Sync selected capabilities in the Integrations tab
            const intCheckboxes = document.querySelectorAll('input[name="agentIntTools"]');
            if (intCheckboxes.length > 0) {
                const selectedTools = [...document.querySelectorAll('input[name="agentIntTools"]:checked')].map(cb => cb.value);
                await authFetch(`/api/agents/${activeAgentId}/tools`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ connected_tools: selectedTools })
                });
                activeAgentData.connected_tools = selectedTools;
                const toolCount = selectedTools.length;
                const badge = document.getElementById('connectedToolsBadge');
                if (badge) badge.textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
            }
            
            const saveBtn = document.getElementById('saveAgentBtn');
            const originalText = saveBtn.textContent;
            saveBtn.textContent = 'Saved!';
            saveBtn.style.backgroundColor = '#22c55e'; // green
            setTimeout(() => {
                saveBtn.textContent = originalText;
                saveBtn.style.backgroundColor = '';
            }, 2000);
            
            loadProjectAgentsList();
        } catch (err) {
            console.error('CRITICAL ERROR saving agent:', err);
            
            const saveBtn = document.getElementById('saveAgentBtn');
            if (saveBtn) {
                const originalText = saveBtn.textContent;
                saveBtn.textContent = 'Error!';
                saveBtn.style.backgroundColor = '#ef4444'; // red
                setTimeout(() => {
                    saveBtn.textContent = originalText;
                    saveBtn.style.backgroundColor = '';
                }, 3000);
            }
            
            alert('Failed to save agent configuration: ' + err.message);
        }
    };

    // Bind Test Preview run
    document.getElementById('runTestBtn')?.addEventListener('click', async () => {
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
        <option value="">Default System Gemini</option>
    `;
    
    // Add custom configs
    llmConfigs.forEach(conf => {
        const optionVal = `custom-${conf.id}`;
        modelSelect.innerHTML += `<option value="${optionVal}">${conf.provider.toUpperCase()} (${conf.model_name})</option>`;
    });
    
    // Select the current one
    if (activeAgentData && (activeAgentData ? activeAgentData.llm_config_id : null)) {
        modelSelect.value = `custom-${(activeAgentData ? activeAgentData.llm_config_id : null)}`;
    } else {
        modelSelect.value = '';
    }
}

// Modify init to trigger config setup
const originalInit = init;
init = async function() {
    await originalInit();
    initAgentConfigForm();
    
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', () => {
            const sidebar = document.querySelector('.ws-sidebar');
            if (sidebar) {
                sidebar.classList.toggle('expanded');
                const textSpan = sidebarToggleBtn.querySelector('.toggle-text');
                if (sidebar.classList.contains('expanded')) {
                    sidebarToggleBtn.querySelector('svg').innerHTML = '<polyline points="11 17 6 12 11 7"></polyline><polyline points="18 17 13 12 18 7"></polyline>';
                    if(textSpan) textSpan.textContent = 'Collapse';
                } else {
                    sidebarToggleBtn.querySelector('svg').innerHTML = '<polyline points="13 17 18 12 13 7"></polyline><polyline points="6 17 11 12 6 7"></polyline>';
                    if(textSpan) textSpan.textContent = 'Expand';
                }
            }
        });
    }

    if (typeof setupAgentDropdown === 'function') {
        setupAgentDropdown();
    }
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
        
        const chatAgentDropdownMenu = document.getElementById('chatAgentDropdownMenu');
        if (chatAgentDropdownMenu) {
            chatAgentDropdownMenu.innerHTML = '<div class="dropdown-group-title" style="padding: 12px 16px 4px; font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">CUSTOM AGENTS</div>';
            data.agents.forEach(agent => {
                const opt = document.createElement('div');
                opt.className = 'dropdown-option';
                opt.style.cssText = 'padding: 8px 16px; font-size: 0.85rem; color: #1e293b; cursor: pointer; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center;';
                opt.dataset.value = agent.id;
                
                const spanName = document.createElement('span');
                spanName.textContent = agent.name;
                
                const spanCheck = document.createElement('span');
                spanCheck.className = 'check-icon';
                spanCheck.style.cssText = 'color: #f97316; display: none; font-weight: bold;';
                spanCheck.innerHTML = '&#10003;';
                
                opt.appendChild(spanName);
                opt.appendChild(spanCheck);
                
                chatAgentDropdownMenu.appendChild(opt);
            });

            chatAgentDropdownMenu.insertAdjacentHTML('beforeend', '<div class="dropdown-group-title" style="padding: 12px 16px 4px; font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">DEFAULT AGENTS</div>');

            
            const defaultAgents = [
                { id: 'null', name: 'System Agent' }
            ];
            defaultAgents.forEach(agent => {
                const opt = document.createElement('div');
                opt.className = 'dropdown-option';
                opt.style.cssText = 'padding: 8px 16px; font-size: 0.85rem; color: #1e293b; cursor: pointer; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center;';
                opt.dataset.value = agent.id;
                
                const spanName = document.createElement('span');
                spanName.textContent = agent.name;
                
                const spanCheck = document.createElement('span');
                spanCheck.className = 'check-icon';
                spanCheck.style.cssText = 'color: #f97316; display: none; font-weight: bold;';
                spanCheck.innerHTML = '&#10003;';
                
                opt.appendChild(spanName);
                opt.appendChild(spanCheck);
                
                chatAgentDropdownMenu.appendChild(opt);
            });
            
            if (typeof updateAgentDropdownSelection === 'function') {
                updateAgentDropdownSelection();
            }
        }

        data.agents.forEach(agent => {
            const card = document.createElement('div');
            card.className = 'agent-hub-card';
            if (agent.id === activeAgentId) {
                card.classList.add('active-card');
            }
            const toolCount = (agent.connected_tools || []).length;
            card.innerHTML = `
                <div class="agent-header" style="position: relative;">
                    <div class="agent-title" style="display:flex; align-items:center; gap:8px;">
                        ${agent.name}
                    </div>
                    <div class="agent-more" style="cursor:pointer; padding:0 4px;">...</div>
                    <div class="agent-context-menu" style="display:none; position:absolute; right:0; top:24px; background:white; border:1px solid #e5e7eb; border-radius:6px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); z-index:10; overflow:hidden; min-width:140px;">
                        <button class="btn-delete-agent" style="display:block; width:100%; text-align:left; padding:8px 12px; background:none; border:none; cursor:pointer; font-size:0.85rem; color:#ef4444;">Delete Agent</button>
                    </div>
                </div>
                <div class="agent-desc">
                    ${agent.description}
                </div>
                <div class="agent-footer">
                    <div class="agent-tools">
                        <div class="tool-box count" style="width:auto; padding:4px 8px; font-weight:500;">${toolCount} Tools / 0 MCP connected</div>
                    </div>
                    <div class="nav-arrow">↗</div>
                </div>
            `;
            
            const moreBtn = card.querySelector('.agent-more');
            const contextMenu = card.querySelector('.agent-context-menu');
            const deleteBtn = card.querySelector('.btn-delete-agent');

            moreBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                document.querySelectorAll('.agent-context-menu').forEach(m => {
                    if (m !== contextMenu) m.style.display = 'none';
                });
                contextMenu.style.display = contextMenu.style.display === 'block' ? 'none' : 'block';
            });

            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                contextMenu.style.display = 'none';
                if (confirm('Are you sure you want to delete this agent?')) {
                    try {
                        await authFetch(`/api/agents/${agent.id}`, { method: 'DELETE' });
                        if (activeAgentId === agent.id) {
                            activeAgentId = null;
                            activeAgentData = null;
                            document.getElementById('agent-config-screen').style.display = 'none';
                            document.getElementById('agents-list-screen').style.display = 'block';
                        }
                        loadProjectAgentsList();
                    } catch (err) {
                        alert('Error deleting agent');
                    }
                }
            });

            document.addEventListener('click', (e) => {
                if (!contextMenu.contains(e.target) && !moreBtn.contains(e.target)) {
                    contextMenu.style.display = 'none';
                }
            });

            card.addEventListener('click', async () => {
                activeAgentId = agent.id;
                const agentRes = await authFetch(`/api/agents/${activeAgentId}`);
                activeAgentData = await agentRes.json();
                
                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agentNameInput').value = activeAgentData.name;
                document.getElementById('agentDescInput').value = activeAgentData.description;
                document.getElementById('personalityPromptInput').value = activeAgentData.system_prompt || '';
                populateAgentModelDropdown();
                
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                document.getElementById('saveAgentBtn').style.display = 'block';
                updateAgentAttachedToolsBox();
                
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
                populateAgentModelDropdown();
                
                document.getElementById('configAgentTitle').textContent = `Configuring: ${activeAgentData.name}`;
                document.getElementById('agents-list-screen').style.display = 'none';
                document.getElementById('agent-config-screen').style.display = 'flex';
                document.getElementById('saveAgentBtn').style.display = 'block';
                updateAgentAttachedToolsBox();
            });
        }
    } catch (e) {
        console.error("Error loading project agents list:", e);
    }
}


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

// MCP Server UI Logic
document.getElementById('addMcpServerBtn')?.addEventListener('click', () => {
    document.getElementById('addMcpModal').style.display = 'flex';
});

document.getElementById('addMcpForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('mcpName').value;
    const cmd = document.getElementById('mcpCommand').value;
    const args = document.getElementById('mcpArgs').value;
    
    document.getElementById('noMcpPlaceholder').style.display = 'none';
    
    const list = document.getElementById('mcpServersList');
    const itemHtml = `
        <div class="agent-integration-item expanded">
            <div class="agent-integration-summary">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:32px; height:32px; background:var(--bg-secondary); border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:16px;">🔌</div>
                    <div class="agent-integration-title">
                        <strong>${name}</strong>
                        <span>${cmd} ${args}</span>
                    </div>
                </div>
                <div class="agent-integration-actions">
                    <span class="agent-integration-badge connected" style="background:#dcfce7; color:#166534; padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">Connected</span>
                </div>
            </div>
        </div>
    `;
    list.insertAdjacentHTML('beforeend', itemHtml);
    
    document.getElementById('addMcpModal').style.display = 'none';
    e.target.reset();
});

// Back to Team navigation
document.getElementById('backToAgentsListBtn')?.addEventListener('click', () => {
    activeAgentId = null;
    activeAgentData = null;
    document.getElementById('agent-config-screen').style.display = 'none';
    document.getElementById('agents-list-screen').style.display = 'block';
    document.getElementById('saveAgentBtn').style.display = 'none';
});
