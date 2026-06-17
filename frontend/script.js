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

// Modal
function openModal() { createModal.classList.add('active'); }
function closeModal() { createModal.classList.remove('active'); createProjectForm.reset(); }
createNewBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
cancelModalBtn?.addEventListener('click', closeModal);

// Load and render projects
async function loadProjects() {
    try {
        const res = await authFetch('/api/projects');
        const data = await res.json();
        document.querySelectorAll('.project-card:not(.create-card)').forEach(c => c.remove());
        data.projects.forEach(project => {
            const card = document.createElement('div');
            card.classList.add('project-card');
            card.innerHTML = `
                <div class="card-header-row" style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <div class="agent-title">${project.name}</div>
                    <button class="delete-project-btn" style="background:none; border:none; cursor:pointer; color:#ef4444; padding:4px; border-radius:4px;" title="Delete Project">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
                <div class="agent-desc">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                    <span>${project.description}</span>
                </div>
            `;
            
            // Handle card click
            card.addEventListener('click', (e) => { 
                if (e.target.closest('.delete-project-btn')) return;
                window.location.href = `/project/${project.id}`; 
            });
            
            // Handle delete button click
            const delBtn = card.querySelector('.delete-project-btn');
            if (delBtn) {
                delBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm(`Are you sure you want to delete the project "${project.name}" and ALL of its related data (agents, workflows, knowledge base, chat history)? This action cannot be undone.`)) {
                        try {
                            const delRes = await authFetch(`/api/projects/${project.id}`, { method: 'DELETE' });
                            if (delRes.ok) {
                                card.remove();
                            } else {
                                alert("Failed to delete project.");
                            }
                        } catch (err) {
                            console.error("Error deleting project:", err);
                            alert("An error occurred while deleting the project.");
                        }
                    }
                });
            }
            
            projectsGrid.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading projects:", e);
    }
}

// Create Project
createProjectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDesc').value;
    
    try {
        const res = await authFetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        const newProject = await res.json();
        window.location.href = `/project/${newProject.id}`;
    } catch (e) {
        console.error("Error creating project:", e);
    }
});

// Search filter
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll('.project-card:not(.create-card)').forEach(card => {
        const title = card.querySelector('.agent-title').textContent.toLowerCase();
        card.style.display = title.includes(query) ? '' : 'none';
    });
});

loadProjects();

// Sync profile from server to fix any stale localStorage username mismatches
(async function syncProfile() {
    try {
        const res = await authFetch('/api/auth/me');
        if (res && res.ok) {
            const userData = await res.json();
            if (userData.username) {
                localStorage.setItem('username', userData.username);
                const userDisplay = document.getElementById('userDisplay');
                if (userDisplay) userDisplay.textContent = userData.username;
                const dropdownUsername = document.getElementById('dropdownUsername');
                if (dropdownUsername) dropdownUsername.textContent = userData.username;
                const userAvatarEl = document.getElementById('userAvatar');
                if (userAvatarEl) userAvatarEl.textContent = userData.username.charAt(0).toUpperCase();
            }
        }
    } catch (e) {
        console.error('Profile sync failed:', e);
    }
})();

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

// --- Global LLM Settings Logic ---
const openGlobalSettingsBtn = document.getElementById('openGlobalSettingsBtn');
const globalSettingsModal = document.getElementById('globalSettingsModal');
const closeGlobalSettingsBtn = document.getElementById('closeGlobalSettingsBtn');
const addGlobalLlmForm = document.getElementById('addGlobalLlmForm');
const globalLlmConfigsList = document.getElementById('globalLlmConfigsList');

if(openGlobalSettingsBtn) {
    openGlobalSettingsBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if(globalSettingsModal) globalSettingsModal.classList.add('active');
        const pd = document.getElementById('profileDropdown');
        if (pd) pd.classList.remove('active');
        loadGlobalLlmConfigs();
    });
}
if(closeGlobalSettingsBtn) {
    closeGlobalSettingsBtn.addEventListener('click', () => {
        if(globalSettingsModal) globalSettingsModal.classList.remove('active');
    });
}

async function loadGlobalLlmConfigs() {
    if(!globalLlmConfigsList) return;
    try {
        const res = await authFetch('/api/settings/llm'); // No project_id = global
        const data = await res.json();
        globalLlmConfigsList.innerHTML = '';

        if (!data.configs || data.configs.length === 0) {
            globalLlmConfigsList.innerHTML = '<div style="font-size:0.85rem; color:var(--text-muted); padding:12px; background:var(--bg-secondary); border-radius:6px;">No global LLMs configured yet.</div>';
            return;
        }
        
        data.configs.forEach(config => {
            const item = document.createElement('div');
            item.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:12px; background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:6px;';
            item.innerHTML = `
                <div>
                    <div style="font-weight:600; font-size:0.9rem; color:var(--text-main);">${config.provider} - ${config.model_name}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">Key: ${config.api_key_masked}</div>
                </div>
                <button class="delete-global-llm-btn" data-id="${config.id}" style="background:none; border:none; cursor:pointer; color:#ef4444; padding:4px;" title="Delete LLM">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            `;
            
            const delBtn = item.querySelector('.delete-global-llm-btn');
            delBtn.addEventListener('click', async () => {
                if(confirm('Delete this global LLM connection?')) {
                    await authFetch(`/api/settings/llm/${config.id}`, { method: 'DELETE' });
                    loadGlobalLlmConfigs();
                }
            });
            globalLlmConfigsList.appendChild(item);
        });
    } catch(err) {
        console.error("Error loading global LLMs:", err);
    }
}

if(addGlobalLlmForm) {
    addGlobalLlmForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const provider = document.getElementById('globalLlmProvider').value;
        const model_name = document.getElementById('globalLlmModel').value;
        const api_key = document.getElementById('globalLlmKey').value;
        
        if (!model_name || !api_key) {
            alert('Please provide model name and API key');
            return;
        }
        
        const saveBtn = document.getElementById('saveGlobalLlmBtn');
        saveBtn.textContent = 'Adding...';
        
        try {
            const res = await authFetch('/api/settings/llm', {
                method: 'POST',
                body: JSON.stringify({ provider, model_name, api_key })
            });
            if(res.ok) {
                document.getElementById('globalLlmModel').value = '';
                document.getElementById('globalLlmKey').value = '';
                loadGlobalLlmConfigs();
            } else {
                alert('Failed to save LLM config');
            }
        } catch(err) {
            console.error("Save LLM err", err);
            alert('Error saving LLM config');
        } finally {
            saveBtn.textContent = 'Add Global LLM';
        }
    });
}

const testGlobalLlmBtn = document.getElementById('testGlobalLlmBtn');
if(testGlobalLlmBtn) {
    testGlobalLlmBtn.addEventListener('click', async () => {
        const provider = document.getElementById('globalLlmProvider').value;
        const model_name = document.getElementById('globalLlmModel').value;
        const api_key = document.getElementById('globalLlmKey').value;
        const statusDiv = document.getElementById('globalLlmTestStatus');
        
        if (!model_name || !api_key) {
            statusDiv.textContent = "Please enter model name and API key to test.";
            statusDiv.style.color = "#ef4444";
            statusDiv.style.display = "block";
            return;
        }
        
        testGlobalLlmBtn.textContent = 'Testing...';
        statusDiv.style.display = "none";
        
        try {
            const res = await authFetch('/api/settings/llm/test', {
                method: 'POST',
                body: JSON.stringify({ provider, model_name, api_key })
            });
            const data = await res.json();
            statusDiv.style.display = "block";
            if (data.status === 'success') {
                statusDiv.textContent = "Success! Connected to model.";
                statusDiv.style.color = "var(--primary-color)";
                statusDiv.style.background = "#d1fae5";
            } else {
                statusDiv.textContent = data.message || "Failed to connect.";
                statusDiv.style.color = "#ef4444";
                statusDiv.style.background = "#fee2e2";
            }
        } catch(err) {
            statusDiv.style.display = "block";
            statusDiv.textContent = "Network error during test.";
            statusDiv.style.color = "#ef4444";
            statusDiv.style.background = "#fee2e2";
        } finally {
            testGlobalLlmBtn.textContent = 'Test Connection';
        }
    });
}
