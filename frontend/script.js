const token = localStorage.getItem('token');
const username = localStorage.getItem('username');

if (username) {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) userDisplay.textContent = username;
    const dropdownUsername = document.getElementById('dropdownUsername');
    if (dropdownUsername) dropdownUsername.textContent = username;
    document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();
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

// Helper for authorized fetches
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

const createNewBtn = document.getElementById('createNewBtn');
const createModal = document.getElementById('createModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelModalBtn = document.getElementById('cancelModalBtn');
const createProjectForm = document.getElementById('createProjectForm');
const projectsGrid = document.getElementById('projectsGrid');
const toolCheckboxes = document.getElementById('toolCheckboxes');

// Modal
function openModal() { createModal.classList.add('active'); }
function closeModal() { createModal.classList.remove('active'); createProjectForm.reset(); }
createNewBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
cancelModalBtn.addEventListener('click', closeModal);
createModal.addEventListener('click', (e) => { if (e.target === createModal) closeModal(); });

// Load available tools into the modal checkboxes
async function loadTools() {
    try {
        const res = await authFetch('/api/tools');
        const data = await res.json();
        toolCheckboxes.innerHTML = '';
        data.tools.forEach(tool => {
            const label = document.createElement('label');
            label.style.cssText = 'display:flex; align-items:center; gap:6px; font-size:0.85rem; cursor:pointer; padding:6px 8px; border:1px solid var(--border-color); border-radius:6px;';
            label.innerHTML = `<input type="checkbox" name="tools" value="${tool.id}"> ${tool.name}`;
            toolCheckboxes.appendChild(label);
        });
    } catch (e) {
        console.error("Error loading tools:", e);
    }
}

// Load and render agents
async function loadAgents() {
    try {
        const res = await authFetch('/api/agents');
        const data = await res.json();
        document.querySelectorAll('.agent-card').forEach(c => c.remove());
        data.agents.forEach(agent => {
            const card = document.createElement('div');
            card.classList.add('project-card', 'agent-card');
            const toolCount = (agent.connected_tools || []).length;
            card.innerHTML = `
                <div class="card-header-row" style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <div class="agent-title">${agent.name}</div>
                </div>
                <div class="agent-desc">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                    <span>${agent.description}</span>
                </div>
                <div class="card-footer-row" style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-top:auto;">
                    <div class="tools-badge-container" style="font-size:0.75rem; color:var(--primary-color); font-weight:600;">${toolCount} tool${toolCount !== 1 ? 's' : ''} connected</div>
                    <button class="delete-project-btn" data-agent-id="${agent.id}">✕</button>
                </div>
            `;
            
            // Delete button binding
            card.querySelector('.delete-project-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Are you sure you want to delete project "${agent.name}"? This will delete all its chat history, knowledge base files, and workflows permanently.`)) {
                    try {
                        const deleteRes = await authFetch(`/api/agents/${agent.id}`, {
                            method: 'DELETE'
                        });
                        if (deleteRes.ok) {
                            loadAgents();
                        } else {
                            const err = await deleteRes.json();
                            alert(`Failed to delete project: ${err.detail || 'Unknown error'}`);
                        }
                    } catch (err) {
                        console.error("Error deleting agent:", err);
                    }
                }
            });

            card.addEventListener('click', () => { window.location.href = `/project/${agent.id}`; });
            projectsGrid.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading agents:", e);
    }
}

// Create agent
createProjectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDesc').value;
    const systemPrompt = document.getElementById('systemPrompt').value;
    const selectedTools = [...document.querySelectorAll('input[name="tools"]:checked')].map(cb => cb.value);

    try {
        const res = await authFetch('/api/agents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, system_prompt: systemPrompt, connected_tools: selectedTools })
        });
        const newAgent = await res.json();
        window.location.href = `/project/${newAgent.id}`;
    } catch (e) {
        console.error("Error creating agent:", e);
    }
});

// Search filter
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll('.agent-card').forEach(card => {
        const title = card.querySelector('.agent-title').textContent.toLowerCase();
        card.style.display = title.includes(query) ? '' : 'none';
    });
});

// View toggle functionality
const viewToggleBtn = document.getElementById('viewToggleBtn');
const gridIcon = document.getElementById('gridIcon');
const listIcon = document.getElementById('listIcon');

let currentViewMode = localStorage.getItem('dashboardViewMode') || 'grid';

function applyViewMode(mode) {
    if (mode === 'list') {
        projectsGrid.classList.add('list-view');
        if (gridIcon) gridIcon.style.display = 'none';
        if (listIcon) listIcon.style.display = 'block';
    } else {
        projectsGrid.classList.remove('list-view');
        if (gridIcon) gridIcon.style.display = 'block';
        if (listIcon) listIcon.style.display = 'none';
    }
    localStorage.setItem('dashboardViewMode', mode);
}

applyViewMode(currentViewMode);

if (viewToggleBtn) {
    viewToggleBtn.addEventListener('click', () => {
        currentViewMode = currentViewMode === 'grid' ? 'list' : 'grid';
        applyViewMode(currentViewMode);
    });
}

// Init
loadTools();
loadAgents();
