with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''
// ==========================================
// Connections Dashboard Logic
// ==========================================
async function loadConnectionsView() {
    const list = document.getElementById('connectionsList');
    if (!list) return;

    list.innerHTML = <div style="text-align:center; padding:40px; color:#94a3b8;"><div style="width:32px;height:32px;border:3px solid #e2e8f0;border-top-color:#6366f1;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 12px;"></div>Loading connections...</div>;

    try {
        const res = await authFetch('/api/credentials');
        const data = await res.json();
        
        const creds = data.credentials || [];
        
        if (creds.length === 0) {
            list.innerHTML = <div style="text-align:center; padding:48px; background:#f8fafc; border-radius:12px; border:2px dashed #e2e8f0;">
                <div style="font-weight:600; color:#475569; margin-bottom:8px;">No connections yet</div>
                <div style="font-size:0.85rem; color:#64748b; margin-bottom:16px;">Connect your external apps to use them in workflows.</div>
                <button class="btn-primary" onclick="openNewConnectionModal()">+ New Connection</button>
            </div>;
            return;
        }

        list.innerHTML = creds.map(c => 
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="width:40px; height:40px; background:#f1f5f9; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:700; color:#475569;">
                        
                    </div>
                    <div>
                        <div style="font-weight:600; font-size:1.05rem; color:#0f172a; margin-bottom:4px;"></div>
                        <div style="font-size:0.8rem; color:#10b981; display:flex; align-items:center; gap:4px;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                            Connected
                        </div>
                    </div>
                </div>
                <button onclick="deleteConnection('')" style="padding:6px 14px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Remove</button>
            </div>
        ).join('');
    } catch (err) {
        console.error('Failed to load connections:', err);
        list.innerHTML = <div style="color:#ef4444; padding:20px; background:#fef2f2; border:1px solid #fecaca; border-radius:8px;">Failed to load connections: </div>;
    }
}

function openNewConnectionModal() {
    document.getElementById('connAppName').value = 'Gmail';
    document.getElementById('connUsername').value = '';
    document.getElementById('connPassword').value = '';
    document.getElementById('newConnectionModal').classList.add('active');
}

async function saveNewConnection() {
    const appName = document.getElementById('connAppName').value;
    const username = document.getElementById('connUsername').value.trim();
    const password = document.getElementById('connPassword').value.trim();

    if (!username || !password) {
        alert('Please enter both username and password.');
        return;
    }

    try {
        const res = await authFetch('/api/credentials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool_name: appName,
                credentials: { username, password }
            })
        });
        if (!res.ok) throw new Error('Failed to save connection');
        
        document.getElementById('newConnectionModal').classList.remove('active');
        loadConnectionsView();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteConnection(appName) {
    if (!confirm(Are you sure you want to remove the connection for ?)) return;
    try {
        const res = await authFetch(/api/credentials/, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete connection');
        loadConnectionsView();
    } catch (err) {
        alert(err.message);
    }
}
'''

if 'loadConnectionsView' not in content:
    content += '\n' + new_code

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
