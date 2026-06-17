import sys
import re

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the entire loadToolsView block
old_load_tools_view_pattern = r"async function loadToolsView\(\) \{.*?(?=// --- Knowledge Base ---)"
import re

# I need to find the start and end of loadToolsView exactly.
old_load_tools_view_start = "async function loadToolsView() {"
old_load_tools_view_end = "// --- Knowledge Base ---"

# Use python to extract
start_idx = content.find(old_load_tools_view_start)
end_idx = content.find(old_load_tools_view_end)

if start_idx != -1 and end_idx != -1:
    old_code = content[start_idx:end_idx]
else:
    print("Could not find loadToolsView")
    sys.exit(1)

new_code = """let selectedAgentTools = new Set();
let allAgentToolsData = [];
let allAgentToolGroups = [];
let allAgentToolStatuses = {};

async function loadToolsView() {
    const res = await authFetch('/api/tools');
    const data = await res.json();
    allAgentToolsData = data.tools || [];
    const connected = agentData.connected_tools || [];
    selectedAgentTools = new Set(connected);

    // Define groups
    allAgentToolGroups = [
        { id: 'servicenow', name: 'ServiceNow', tools: ['servicenow_incidents', 'servicenow_tables'] },
        { id: 'salesforce', name: 'Salesforce', tools: ['salesforce_query', 'salesforce_create'] },
        { id: 'gmail', name: 'Gmail', tools: ['gmail_read', 'gmail_send'] },
        { id: 'jira', name: 'Jira', tools: ['jira_issues'] },
        { id: 'outlook', name: 'Outlook', tools: ['outlook_calendar', 'outlook_email'], systemDefault: true },
        { id: 'google_search_tool', name: 'Web Search', tools: ['google_search'], systemDefault: true }
    ];

    allAgentToolStatuses = {};
    for (const group of allAgentToolGroups) {
        if (group.systemDefault) {
            allAgentToolStatuses[group.id] = true;
            continue;
        }
        try {
            const statusRes = await authFetch(`/api/credentials/${group.id}`);
            const statusData = await statusRes.json();
            allAgentToolStatuses[group.id] = statusData.configured;
        } catch (err) {
            allAgentToolStatuses[group.id] = false;
        }
    }

    renderAgentToolsGrid();

    // Bind search
    const searchInput = document.getElementById('agentToolsSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterAgentTools(e.target.value);
        });
    }
}

function renderAgentToolsGrid() {
    const grid = document.getElementById('agentToolsGrid');
    if (!grid) return;

    let html = '';
    for (const group of allAgentToolGroups) {
        const isConnected = allAgentToolStatuses[group.id];
        
        let countSelected = 0;
        group.tools.forEach(t => { if (selectedAgentTools.has(t)) countSelected++; });

        const countBadge = countSelected > 0 
            ? `<span style="position:absolute; top:-6px; right:-6px; background:#10b981; color:white; font-size:0.7rem; font-weight:700; border-radius:10px; padding:2px 6px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">${countSelected} tools</span>`
            : '';

        html += `
            <div class="agent-tool-grid-item" data-group-name="${group.name.toLowerCase()}" onclick="openAgentToolConfigModal('${group.id}')" style="position:relative; background:white; border:1px solid #e2e8f0; border-radius:10px; padding:16px 12px; text-align:center; cursor:pointer; transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s; display:flex; flex-direction:column; align-items:center; gap:8px;" onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.06)'; this.style.borderColor='#cbd5e1';" onmouseout="this.style.transform='none'; this.style.boxShadow='none'; this.style.borderColor='#e2e8f0';">
                ${countBadge}
                <div style="width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);">${getAppIconMarkup(group.id)}</div>
                <div style="font-weight:600; font-size:0.85rem; color:#1e293b;">${group.name}</div>
                <div style="font-size:0.65rem; color:${isConnected ? '#10b981' : '#ef4444'}; font-weight:600;">
                    ${isConnected ? '● Connected' : '○ Disconnected'}
                </div>
            </div>
        `;
    }
    grid.innerHTML = html;
}

function filterAgentTools(query) {
    const q = query.toLowerCase();
    const items = document.querySelectorAll('.agent-tool-grid-item');
    items.forEach(item => {
        const name = item.getAttribute('data-group-name');
        if (name.includes(q)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

window.openAgentToolConfigModal = function(groupId) {
    const group = allAgentToolGroups.find(g => g.id === groupId);
    if (!group) return;

    const isConnected = allAgentToolStatuses[groupId];
    const groupTools = allAgentToolsData.filter(t => group.tools.includes(t.id));

    // Render Header
    const header = document.getElementById('agentToolModalHeader');
    header.innerHTML = `
        <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center;">${getAppIconMarkup(group.id)}</div>
        <h2 style="margin:0; font-size:1.25rem; font-weight:700; color:#0f172a;">${group.name}</h2>
    `;

    // Render Status bar
    const statusDiv = document.getElementById('agentToolModalStatus');
    const manageBtn = document.getElementById('agentToolModalManageBtn');
    
    if (isConnected) {
        statusDiv.innerHTML = `<span style="color:#10b981; font-weight:700; font-size:0.9rem;">● Connection Active</span><br><span style="color:#64748b; font-size:0.8rem;">You can safely enable the tools below.</span>`;
    } else {
        statusDiv.innerHTML = `<span style="color:#ef4444; font-weight:700; font-size:0.9rem;">○ Not Connected</span><br><span style="color:#64748b; font-size:0.8rem;">Link your account to enable capabilities.</span>`;
    }
    
    if (group.systemDefault) {
        manageBtn.style.display = 'none';
    } else {
        manageBtn.style.display = 'block';
        manageBtn.textContent = isConnected ? 'Manage Connection' : 'Connect Account';
        manageBtn.onclick = () => {
            closeAgentToolConfigModal();
            openManageConnectionsModal(group.id);
        };
    }

    // Render Body
    const body = document.getElementById('agentToolModalBody');
    let bodyHtml = `<div class="tools-capabilities-grid">`;
    groupTools.forEach(tool => {
        const isChecked = selectedAgentTools.has(tool.id) ? 'checked' : '';
        const isDisabled = !isConnected ? 'disabled' : '';
        bodyHtml += `
            <div class="tools-capability-card" style="${!isConnected ? 'opacity: 0.6; cursor: not-allowed;' : ''}">
                <input type="checkbox" class="tools-capability-checkbox modal-tool-cb" data-tool-id="${tool.id}" ${isChecked} ${isDisabled}>
                <div class="tools-capability-info">
                    <span class="tools-capability-name">${tool.name}</span>
                    <span class="tools-capability-desc">${tool.description}</span>
                </div>
            </div>
        `;
    });
    bodyHtml += `</div>`;
    body.innerHTML = bodyHtml;

    // Add checkbox event listeners to update Set
    document.querySelectorAll('.modal-tool-cb').forEach(cb => {
        cb.addEventListener('change', (e) => {
            if (e.target.checked) {
                selectedAgentTools.add(e.target.dataset.toolId);
            } else {
                selectedAgentTools.delete(e.target.dataset.toolId);
            }
            renderAgentToolsGrid(); // Update the tool count badge in grid
        });
    });

    document.getElementById('agentToolConfigModal').style.display = 'flex';
};

window.closeAgentToolConfigModal = function() {
    document.getElementById('agentToolConfigModal').style.display = 'none';
};

// Save Tools Button Replacement
document.getElementById('saveToolsBtn').addEventListener('click', async () => {
    const btn = document.getElementById('saveToolsBtn');
    btn.textContent = 'Saving...';
    btn.disabled = true;

    try {
        const res = await authFetch(`/api/agents/${agentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: agentData.name,
                prompt: agentData.prompt,
                connected_tools: Array.from(selectedAgentTools)
            })
        });

        if (res.ok) {
            agentData = await res.json();
            btn.textContent = 'Saved!';
            const toolCount = (agentData.connected_tools || []).length;
            document.getElementById('connectedToolsBadge').textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
            setTimeout(() => {
                btn.textContent = 'Save Tools';
                btn.disabled = false;
            }, 2000);
        } else {
            const data = await res.json();
            alert('Failed to save tools: ' + (data.detail || data.message || "Unknown error"));
            btn.textContent = 'Save Tools';
            btn.disabled = false;
        }
    } catch (err) {
        alert("Save failed: " + err.message);
        btn.textContent = 'Save Tools';
        btn.disabled = false;
    }
});

// Remove old saveToolsBtn listener
"""

content = content.replace(old_code, new_code + "\n\n")

# Now I must strip out the old saveToolsBtn listener block which is right after old_code (or inside it?).
# Let's check where saveToolsBtn was. In the original file, it was inside a big block.
old_save_btn_listener = """document.getElementById('saveToolsBtn').addEventListener('click', async () => {
    const btn = document.getElementById('saveToolsBtn');
    btn.textContent = 'Saving...';
    btn.disabled = true;

    const checkedBoxes = document.querySelectorAll('input[name="agentTools"]:checked');
    const connectedTools = Array.from(checkedBoxes).map(cb => cb.value);

    try {
        const res = await authFetch(`/api/agents/${agentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: agentData.name,
                prompt: agentData.prompt,
                connected_tools: connectedTools
            })
        });

        if (res.ok) {
            agentData = await res.json();
            btn.textContent = 'Saved!';
            const toolCount = (agentData.connected_tools || []).length;
            document.getElementById('connectedToolsBadge').textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
            setTimeout(() => {
                btn.textContent = 'Save Tools';
                btn.disabled = false;
            }, 2000);
        } else {
            btn.textContent = 'Save Tools';
            btn.disabled = false;
        }
    } catch (e) {
        btn.textContent = 'Save Tools';
        btn.disabled = false;
    }
});"""

if old_save_btn_listener in content:
    content = content.replace(old_save_btn_listener, "")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched project.js successfully")
