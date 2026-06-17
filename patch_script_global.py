import sys

js_append = """
// --- Global LLM Settings Logic ---
const openGlobalSettingsBtn = document.getElementById('openGlobalSettingsBtn');
const globalSettingsModal = document.getElementById('globalSettingsModal');
const closeGlobalSettingsBtn = document.getElementById('closeGlobalSettingsBtn');
const addGlobalLlmForm = document.getElementById('addGlobalLlmForm');
const globalLlmConfigsList = document.getElementById('globalLlmConfigsList');

if(openGlobalSettingsBtn) {
    openGlobalSettingsBtn.addEventListener('click', () => {
        globalSettingsModal.classList.add('active');
        loadGlobalLlmConfigs();
    });
}
if(closeGlobalSettingsBtn) {
    closeGlobalSettingsBtn.addEventListener('click', () => {
        globalSettingsModal.classList.remove('active');
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
"""

with open('frontend/script.js', 'a', encoding='utf-8') as f:
    f.write("\n" + js_append)
print("script.js appended.")
