import sys

missing_forms = """
<div id="settingsFormsContainer" style="display:none;">
    <!-- Salesforce -->
    <div class="settings-config-panel" id="settings-panel-salesforce">
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Instance URL</label><input type="text" id="sfUrl" placeholder="https://your-instance.salesforce.com" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Username</label><input type="text" id="sfUser" placeholder="user@company.com" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Password</label><input type="password" id="sfPass" placeholder="password" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Security Token</label><input type="password" id="sfToken" placeholder="token" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
            <button type="button" class="btn-cancel" id="testSfCredsBtn">Test Connection</button>
            <button type="button" class="btn-primary" id="saveSfCreds">Save Credentials</button>
        </div>
        <div id="sfTestStatus" style="margin-top:12px; font-size:0.85rem; display:none; padding:12px; border-radius:6px;"></div>
    </div>

    <!-- ServiceNow -->
    <div class="settings-config-panel" id="settings-panel-servicenow">
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Instance URL</label><input type="text" id="snUrl" placeholder="https://dev12345.service-now.com" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Client ID</label><input type="text" id="snClientId" placeholder="Client ID" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Client Secret</label><input type="password" id="snClientSecret" placeholder="Client Secret" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Username</label><input type="text" id="snUser" placeholder="admin" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Password</label><input type="password" id="snPass" placeholder="password" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
            <button type="button" class="btn-cancel" id="testSnCredsBtn">Test Connection</button>
            <button type="button" class="btn-primary" id="saveSnCreds">Save Credentials</button>
        </div>
        <div id="snTestStatus" style="margin-top:12px; font-size:0.85rem; display:none; padding:12px; border-radius:6px;"></div>
    </div>

    <!-- Gmail -->
    <div class="settings-config-panel" id="settings-panel-gmail">
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Gmail Username</label><input type="text" id="gmUser" placeholder="user@gmail.com" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">App Password</label><input type="password" id="gmToken" placeholder="App Password" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
            <button type="button" class="btn-cancel" id="testGmCredsBtn">Test Connection</button>
            <button type="button" class="btn-primary" id="saveGmCreds">Save Credentials</button>
        </div>
        <div id="gmTestStatus" style="margin-top:12px; font-size:0.85rem; display:none; padding:12px; border-radius:6px;"></div>
    </div>

    <!-- Jira -->
    <div class="settings-config-panel" id="settings-panel-jira">
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Instance URL</label><input type="text" id="jrUrl" placeholder="https://company.atlassian.net" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">Username / Email</label><input type="text" id="jrUser" placeholder="user@company.com" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div class="form-group" style="margin-bottom:12px;"><label style="display:block; font-size:0.85rem; font-weight:600; margin-bottom:6px;">API Token</label><input type="password" id="jrToken" placeholder="token" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:6px;"></div>
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
            <button type="button" class="btn-cancel" id="testJrCredsBtn">Test Connection</button>
            <button type="button" class="btn-primary" id="saveJrCreds">Save Credentials</button>
        </div>
        <div id="jrTestStatus" style="margin-top:12px; font-size:0.85rem; display:none; padding:12px; border-radius:6px;"></div>
    </div>
</div>
"""

with open('frontend/project.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'id="settingsFormsContainer"' not in html:
    html = html.replace('</body>', missing_forms + '\n</body>')
    html = html.replace('v=31', 'v=32')
    with open('frontend/project.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Forms injected successfully.")
else:
    print("Forms already exist.")
