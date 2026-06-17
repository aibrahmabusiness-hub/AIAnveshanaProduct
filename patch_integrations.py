import sys

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

# We will define a global groups array so both views can use it
groups_array = """
const INTEGRATION_GROUPS = [
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

function openIntegrationAuthModal(toolId) {
    const modal = document.getElementById('integrationAuthModal');
    const modalBody = document.getElementById('integrationAuthModalBody');
    const title = document.getElementById('integrationAuthModalTitle');
    const sourcePanel = document.getElementById(`settings-panel-${toolId}`);
    
    if (!sourcePanel) {
        alert("Configuration panel for this integration is not available.");
        return;
    }
    
    modalBody.dataset.toolId = toolId;
    const groupName = INTEGRATION_GROUPS.find(g => g.id === toolId)?.name || toolId;
    title.textContent = `Connect ${groupName}`;
    
    modalBody.innerHTML = '';
    modalBody.appendChild(sourcePanel);
    sourcePanel.classList.add('active');
    
    document.getElementById('integrationAuthTestBtn').style.display = 'none';
    document.getElementById('integrationAuthSaveBtn').style.display = 'none';
    
    modal.classList.add('active');
}

if (document.getElementById('closeIntegrationAuthModalBtn')) {
    document.getElementById('closeIntegrationAuthModalBtn').addEventListener('click', () => {
        const modal = document.getElementById('integrationAuthModal');
        const modalBody = document.getElementById('integrationAuthModalBody');
        const toolId = modalBody.dataset.toolId;
        if (toolId) {
            const sourcePanel = document.getElementById(`settings-panel-${toolId}`);
            const originalParent = document.getElementById('settingsFormsContainer');
            if (originalParent && sourcePanel) {
                sourcePanel.classList.remove('active');
                originalParent.appendChild(sourcePanel);
            }
        }
        modal.classList.remove('active');
    });
}

async function renderIntegrationsList(containerId, isAgentContext) {
    const listContainer = document.getElementById(containerId);
    if (!listContainer) return;
    
    const res = await authFetch('/api/tools');
    const data = await res.json();
    const connected = agentData ? (agentData.connected_tools || []) : [];
    
    const statuses = {};
    for (const group of INTEGRATION_GROUPS) {
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
    
    listContainer.innerHTML = INTEGRATION_GROUPS.map(group => {
        const isConnected = statuses[group.id];
        const badgeClass = isConnected ? 'agent-integration-badge connected' : 'agent-integration-badge unconfigured';
        const badgeText = isConnected ? 'Connected' : 'Not Configured';
        
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
                openIntegrationAuthModal(group.id);
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
                agentData.connected_tools = selectedTools;
                const toolCount = selectedTools.length;
                const badge = document.getElementById('connectedToolsBadge');
                if (badge) badge.textContent = `${toolCount} tool${toolCount !== 1 ? 's' : ''} connected`;
                if (typeof updateAgentAttachedToolsBox === 'function') updateAgentAttachedToolsBox();
            });
        });
    }
}
"""

# We need to replace loadAgentIntegrationsView and loadToolsView
import re

# 1. Replace loadToolsView
tools_view_pattern = re.compile(r'async function loadToolsView\(\)\s*\{.*?\n\}\n', re.DOTALL)
new_tools_view = """async function loadToolsView() {
    const toolsList = document.getElementById('agentToolsGrid');
    if (toolsList) {
        toolsList.style.display = 'block';
        await renderIntegrationsList('agentToolsGrid', false);
    }
}
"""
text = tools_view_pattern.sub(new_tools_view, text)

# 2. Replace loadAgentIntegrationsView
integrations_view_pattern = re.compile(r'async function loadAgentIntegrationsView\(\)\s*\{.*?updateAgentAttachedToolsBox\(\);\s*\}\);\s*\}\);\s*\}', re.DOTALL)
new_integrations_view = """async function loadAgentIntegrationsView() {
    await renderIntegrationsList('agentIntegrationsList', true);
}"""

if integrations_view_pattern.search(text):
    text = integrations_view_pattern.sub(new_integrations_view, text)
else:
    print("Could not find loadAgentIntegrationsView pattern")

# Prepend the new definitions just after the global variables
text = text.replace('const AVAILABLE_TOOLS = [', groups_array + '\n\nconst AVAILABLE_TOOLS = [')

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=30', 'v=31')
with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patch complete")
