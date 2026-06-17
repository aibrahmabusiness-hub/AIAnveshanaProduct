import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add sidebar tab
nav_item = '''            <div class="ws-nav-item" data-view="connections">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                Connections
            </div>'''

if 'data-view="connections"' not in html:
    html = html.replace('<div class="ws-nav-item" data-view="workflows">', nav_item + '\n            <div class="ws-nav-item" data-view="workflows">')

# 2. Add Connections view
connections_view = '''            <!-- Connections View -->
            <div class="ws-view" id="view-connections" style="display:none;">
                <div class="ws-panel" style="max-width:800px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <div>
                            <h2>App Connections</h2>
                            <p style="color:var(--text-muted);">Manage authentication and credentials for external services.</p>
                        </div>
                        <button class="btn-primary" onclick="openNewConnectionModal()">+ New Connection</button>
                    </div>
                    <div id="connectionsList" style="display:flex; flex-direction:column; gap:16px;">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>'''

if 'id="view-connections"' not in html:
    html = html.replace('<!-- Workflows View -->', connections_view + '\n\n            <!-- Workflows View -->')

# 3. Add Modal for New Connection
connection_modal = '''    <!-- New Connection Modal -->
    <div class="modal" id="newConnectionModal">
        <div class="modal-content" style="max-width:500px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;border-bottom:1px solid #e2e8f0;padding-bottom:12px;">
                <h3 style="margin:0;font-size:1.2rem;color:#0f172a;">New Connection</h3>
                <button onclick="document.getElementById('newConnectionModal').classList.remove('active')" style="background:none;border:none;font-size:1.5rem;color:#94a3b8;cursor:pointer;">&times;</button>
            </div>
            <div class="form-group">
                <label>App / Tool</label>
                <select id="connAppName" style="width:100%;padding:10px;border:1px solid #e2e8f0;border-radius:6px;outline:none;background:#f8fafc;">
                    <option value="Gmail">Gmail</option>
                    <option value="ServiceNow">ServiceNow</option>
                    <option value="Jira">Jira</option>
                    <option value="Slack">Slack</option>
                    <option value="Custom">Custom / Other</option>
                </select>
            </div>
            
            <div style="margin:20px 0;">
                <div style="font-weight:600; font-size:0.9rem; color:#475569; margin-bottom:12px;">Authentication Method</div>
                
                <!-- Direct Connect (OAuth) -->
                <div style="border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:12px; cursor:pointer; display:flex; align-items:center; gap:12px; transition:border-color 0.2s;" onmouseover="this.style.borderColor='#6366f1'" onmouseout="this.style.borderColor='#e2e8f0'" onclick="alert('OAuth Direct Connect flow will open in a popup.')">
                    <div style="width:40px; height:40px; background:#eff6ff; border-radius:8px; display:flex; align-items:center; justify-content:center;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3"></path><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                    </div>
                    <div>
                        <div style="font-weight:600; color:#0f172a;">Direct Connect (Recommended)</div>
                        <div style="font-size:0.8rem; color:#64748b;">Sign in directly via OAuth</div>
                    </div>
                </div>

                <!-- Username/App Password -->
                <div id="connAppPasswordField" style="border:1px solid #e2e8f0; border-radius:8px; padding:16px;">
                    <div style="font-weight:600; color:#0f172a; margin-bottom:12px;">Username & App Password</div>
                    <div class="form-group">
                        <label>Username / Email</label>
                        <input type="text" id="connUsername" placeholder="e.g. user@gmail.com">
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>App Password</label>
                        <input type="password" id="connPassword" placeholder="16-character app password">
                        <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">Do not use your main account password. Use a dedicated App Password.</div>
                    </div>
                </div>
            </div>

            <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:24px;">
                <button class="btn-secondary" onclick="document.getElementById('newConnectionModal').classList.remove('active')">Cancel</button>
                <button class="btn-primary" onclick="saveNewConnection()">Save Connection</button>
            </div>
        </div>
    </div>'''

if 'id="newConnectionModal"' not in html:
    html = html.replace('<!-- End Modals -->', connection_modal + '\n\n    <!-- End Modals -->')

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.html', 'w', encoding='utf-8') as f:
    f.write(html)
