import sys
import re

with open('frontend/project.js', 'r', encoding='utf-8') as f:
    text = f.read()

js_code = """
let currentAccountsModalToolId = null;

async function showConnectionAccountsModal(toolId) {
    currentAccountsModalToolId = toolId;
    const modal = document.getElementById('connectionAccountsModal');
    if (!modal) {
        alert("Connection modal not found in HTML!");
        return;
    }
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
        const accounts = await res.json();
        
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
    
    const dynamicFields = document.getElementById('connDynamicFields');
    dynamicFields.innerHTML = '';
    
    const sourcePanel = document.getElementById(`settings-panel-${currentAccountsModalToolId}`);
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
"""

# CAREFULLY REPLACE openIntegrationAuthModal
pattern1 = r"function openIntegrationAuthModal\(toolId\) \{.*?modal\.classList\.add\('active'\);\n\}"
text = re.sub(pattern1, js_code, text, flags=re.DOTALL)

pattern2 = r"if \(document\.getElementById\('closeIntegrationAuthModalBtn'\)\) \{\n    document\.getElementById\('closeIntegrationAuthModalBtn'\)\.addEventListener\('click', \(\) => \{.*?\n    \}\);\n\}"
text = re.sub(pattern2, "", text, flags=re.DOTALL)

# Now modify renderIntegrationsList
old_status_fetch = """        try {
            const statusRes = await authFetch(`/api/credentials/${group.id}`);
            const statusData = await statusRes.json();
            statuses[group.id] = statusData.configured;
        } catch (err) {
            statuses[group.id] = false;
        }"""

new_status_fetch = """        try {
            const accRes = await authFetch(`/api/credentials/${group.id}/accounts`);
            const accs = await accRes.json();
            statuses[group.id] = Array.isArray(accs) ? accs.length : 0;
        } catch (err) {
            statuses[group.id] = 0;
        }"""
text = text.replace(old_status_fetch, new_status_fetch)

# Modify render html
old_html_logic = """        const isConnected = statuses[group.id];
        const badgeClass = isConnected ? 'agent-integration-badge connected' : 'agent-integration-badge unconfigured';
        const badgeText = isConnected ? 'Connected' : 'Not Configured';"""

new_html_logic = """        const numAccounts = statuses[group.id];
        const isConnected = numAccounts > 0;
        const badgeClass = isConnected ? 'agent-integration-badge connected' : 'agent-integration-badge unconfigured';
        const badgeText = isConnected ? `${numAccounts} Account${numAccounts !== 1 ? 's' : ''} Connected` : 'Not Configured';"""
text = text.replace(old_html_logic, new_html_logic)

# Replace 'openIntegrationAuthModal(group.id);' with 'showConnectionAccountsModal(group.id);'
text = text.replace('openIntegrationAuthModal(group.id);', 'showConnectionAccountsModal(group.id);')

with open('frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=33', 'v=34')
with open('frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated JS safely.")
