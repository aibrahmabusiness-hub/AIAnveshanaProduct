import sys

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

# I need to find the `loadAgents();` line and the `if (!data.configs` line.
# Everything between them was deleted. Let's fix it.

correct_block = """
// Init
loadTools();
loadAgents();

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
"""

# Replace the broken area
import re
text = re.sub(r'// Init\s*loadTools\(\);\s*loadAgents\(\);\s*if \(!data\.configs', correct_block + "\n        if (!data.configs", text)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(text)
print("script.js patched successfully.")
