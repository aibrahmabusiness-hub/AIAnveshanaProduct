import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Execute Button
new_btns = """<button class="btn" style="padding:8px 16px; border:1px solid #e2e8f0; border-radius:8px; background:#fff; cursor:pointer;" id="cancelWorkflowModalBtn" onclick="closeWorkflowEditor()">Cancel</button>
                    <button class="btn" style="padding:8px 16px; background:#6366f1; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer;" id="saveWorkflowBtn" onclick="saveWorkflow()">Save Workflow</button>
                    <button class="btn" style="padding:8px 16px; background:#22c55e; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer; margin-left:8px;" id="executeWorkflowBtn" onclick="executeWorkflow()">? Run Workflow</button>"""
html = re.sub(r'<button class="btn" style="padding:8px 16px; border:1px solid #e2e8f0; border-radius:8px; \r?\n?background:#fff; cursor:pointer;" id="cancelWorkflowModalBtn" onclick="closeWorkflowEditor\(\)">Cancel</button>\s*<button class="btn" style="padding:8px 16px; background:#6366f1; color:white; border:none; \r?\n?border-radius:8px; font-weight:600; cursor:pointer;" id="saveWorkflowBtn" onclick="saveWorkflow\(\)">Save \r?\n?Workflow</button>', new_btns, html, flags=re.DOTALL)

# 2. Modify properties panel to have tabs
new_props = """<div id="properties-panel" style="width:340px; background:#fff; border-left:1px solid #e2e8f0; padding:16px; display:none; flex-direction:column; overflow-y:auto; flex-shrink:0;">
                      <h3 style="margin:0 0 16px 0; font-size:1rem; font-weight:700; color:#0f172a;">Step Configuration</h3>
                      
                      <!-- Tabs -->
                      <div style="display:flex; border-bottom:1px solid #e2e8f0; margin-bottom:16px;">
                          <div id="tab-parameters" style="padding:8px 16px; cursor:pointer; font-weight:600; color:#4f46e5; border-bottom:2px solid #4f46e5;">Parameters</div>
                          <div id="tab-testnode" style="padding:8px 16px; cursor:pointer; font-weight:600; color:#64748b;">Test Step</div>
                      </div>

                      <div id="nodeInspectHeader" style="margin-bottom:16px;">
                          <!-- icon and title populated here -->
                      </div>
                      
                      <div id="tab-content-parameters">
                          <div id="nodeInspectContent">
                              <!-- dynamic form fields -->
                          </div>
                      </div>
                      
                      <div id="tab-content-testnode" style="display:none;">
                          <button class="btn" style="width:100%; padding:8px 16px; background:#3b82f6; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer; margin-bottom:12px;" id="testNodeBtn" onclick="testCurrentNode()">? Test Step</button>
                          <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">OUTPUT DATA</div>
                          <pre id="testNodeOutput" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; font-size:0.8rem; color:#334155; overflow-x:auto; min-height:100px;">Run the step to see output.</pre>
                      </div>
                  </div>"""
html = re.sub(r'<div id="properties-panel".*?id="nodeInspectContent">.*?</div>\s*</div>', new_props, html, flags=re.DOTALL)

# 3. Dock debug console to bottom instead of full screen modal
# The original debugConsole is style="position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(15,23,42,0.9); z-index:9999; display:none; flex-direction:column;"
new_debug = """<!-- Debug Console (Docked to bottom) -->
    <div id="debugConsole" style="position:absolute; bottom:0; left:300px; right:340px; height:250px; background:#1e293b; border-top:2px solid #334155; z-index:1000; display:none; flex-direction:column; box-shadow: 0 -4px 10px rgba(0,0,0,0.1);">
        <div style="padding:12px 16px; background:#0f172a; color:#f8fafc; font-weight:600; display:flex; justify-content:space-between; align-items:center;">
            <span>Execution Logs</span>
            <button onclick="document.getElementById('debugConsole').style.display='none'" style="background:none; border:none; color:#94a3b8; font-size:1.2rem; cursor:pointer;">&times;</button>
        </div>
        <div id="debugConsoleContent" style="flex:1; overflow-y:auto; padding:16px; font-family:monospace; font-size:0.85rem; color:#cbd5e1; line-height:1.5;">
            <!-- logs -->
        </div>
    </div>"""

html = re.sub(r'<!-- Debug Console -->.*?<div id="debugConsoleContent".*?</div>\s*</div>', new_debug, html, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.html", "w", encoding="utf-8") as f:
    f.write(html)
