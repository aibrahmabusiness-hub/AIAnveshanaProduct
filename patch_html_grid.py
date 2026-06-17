import sys

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the tools list HTML
old_tools_html = """<div class="ws-view" id="view-tools">
                <div class="ws-panel">
                    <h2>Connected Tools</h2>
                    <p style="color:var(--text-muted); margin-bottom:20px;">Select which tools this agent can use.</p>
                    <div id="toolsList"></div>
                    <button class="btn-primary" id="saveToolsBtn" style="margin-top:20px;">Save Tools</button>
                </div>
            </div>"""

new_tools_html = """<div class="ws-view" id="view-tools">
                <div class="ws-panel">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div>
                            <h2>Agent Tools</h2>
                            <p style="color:var(--text-muted);">Manage connections and enable capabilities for this agent.</p>
                        </div>
                        <button class="btn-primary" id="saveToolsBtn">Save Tools</button>
                    </div>
                    
                    <input type="text" id="agentToolsSearch" placeholder="Search apps (e.g., Gmail, Jira)..." style="width:100%; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 24px; font-size: 0.95rem; box-sizing: border-box; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='#6366f1';" onblur="this.style.borderColor='#e2e8f0';">
                    
                    <div id="agentToolsGrid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px;"></div>
                </div>
            </div>"""

if old_tools_html in content:
    content = content.replace(old_tools_html, new_tools_html)

# 2. Add the agentToolConfigModal at the end of the file before script tag
modal_html = """
    <!-- Agent Tool Config Modal -->
    <div id="agentToolConfigModal" style="display:none; position:fixed; inset:0; background:rgba(15,23,42,0.6); z-index:100; align-items:center; justify-content:center; backdrop-filter:blur(4px);">
        <div style="background:white; width:100%; max-width:600px; max-height:85vh; border-radius:16px; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.25); overflow:hidden;">
            <div style="padding:20px 24px; border-bottom:1px solid #f1f5f9; display:flex; justify-content:space-between; align-items:center; background:#f8fafc;">
                <div id="agentToolModalHeader" style="display: flex; align-items: center; gap: 12px;">
                    <!-- Logo and Name populated by JS -->
                </div>
                <button onclick="closeAgentToolConfigModal()" style="background:none; border:none; color:#94a3b8; cursor:pointer; padding:8px; border-radius:50%;" onmouseover="this.style.background='#e2e8f0'; this.style.color='#475569'" onmouseout="this.style.background='none'; this.style.color='#94a3b8'">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
            
            <div style="padding: 24px; border-bottom: 1px solid #f1f5f9; background: white; display: flex; justify-content: space-between; align-items: center;">
                <div id="agentToolModalStatus"></div>
                <button id="agentToolModalManageBtn" style="background:var(--primary-color); color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:0.85rem; font-weight:600; box-shadow:0 2px 4px rgba(0,0,0,0.1);"></button>
            </div>
            
            <div id="agentToolModalBody" style="padding:24px; overflow-y:auto; flex:1; background:#f8fafc;">
                <!-- Capabilities populated by JS -->
            </div>
            
            <div style="padding:16px 24px; border-top:1px solid #e2e8f0; display:flex; justify-content:flex-end; background:white;">
                <button onclick="closeAgentToolConfigModal()" style="padding:8px 24px; background:var(--primary-color); color:white; border:none; border-radius:8px; font-size:0.875rem; font-weight:600; cursor:pointer;">
                    Done
                </button>
            </div>
        </div>
    </div>
"""

if "agentToolConfigModal" not in content:
    content = content.replace("<script src=\"/project.js", modal_html + "\n    <script src=\"/project.js")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched project.html successfully")
