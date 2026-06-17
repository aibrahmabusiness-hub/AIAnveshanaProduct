import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update loadWorkflowsView
old_load = """        const workflows = data.workflows || [];
        
        if (workflows.length === 0) {
            list.innerHTML = <div style="text-align:center; padding:48px; background:#f8fafc; border-radius:12px; border:2px dashed #e2e8f0;">
                <div style="font-weight:600; color:#475569; margin-bottom:8px;">No workflows found</div>
                <div style="font-size:0.85rem; color:#64748b; margin-bottom:16px;">Create your first workflow to automate tasks.</div>
                <button class="btn-primary" onclick="createNewWorkflow()">+ Create Workflow</button>
            </div>;
            return;
        }

        list.innerHTML = workflows.map(wf => 
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; display:flex; justify-content:space-between; align-items:center; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.05)'" onmouseout="this.style.boxShadow='none'">
                <div>
                    <div style="font-weight:600; font-size:1.05rem; color:#0f172a; margin-bottom:4px;"></div>
                    <div style="font-size:0.8rem; color:#64748b; display:flex; gap:12px; align-items:center;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <div onclick="event.stopPropagation(); toggleWorkflowStatus(, '')" style="width:36px; height:20px; border-radius:10px; position:relative; cursor:pointer; transition:background-color 0.2s; background:;">
                                <div style="width:16px; height:16px; border-radius:50%; background:white; position:absolute; top:2px; transition:left 0.2s; left:; box-shadow:0 1px 2px rgba(0,0,0,0.1);"></div>
                            </div>
                            <span style="font-weight:600; color:; text-transform:capitalize;"></span>
                        </div>
                        <span>ID: </span>
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button onclick="openWorkflowEditor()" style="padding:6px 14px; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Edit</button>
                    <button onclick="deleteWorkflow()" style="padding:6px 14px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Delete</button>
                </div>
            </div>
        ).join('');
    } catch (err) {"""

new_load = """        window.currentWorkflows = data.workflows || [];
        window.renderWorkflowsList();
    } catch (err) {"""

if old_load in js:
    js = js.replace(old_load, new_load)
    print("Replaced loadWorkflowsView internals.")
else:
    print("WARNING: Could not find old_load")

# 2. Add window.renderWorkflowsList
render_func = """
window.renderWorkflowsList = function() {
    const list = document.getElementById('workflowsList');
    if (!list) return;
    const workflows = window.currentWorkflows || [];
    
    if (workflows.length === 0) {
        list.innerHTML = <div style="text-align:center; padding:48px; background:#f8fafc; border-radius:12px; border:2px dashed #e2e8f0;">
            <div style="font-weight:600; color:#475569; margin-bottom:8px;">No workflows found</div>
            <div style="font-size:0.85rem; color:#64748b; margin-bottom:16px;">Create your first workflow to automate tasks.</div>
            <button class="btn-primary" onclick="createNewWorkflow()">+ Create Workflow</button>
        </div>;
        return;
    }

    list.innerHTML = workflows.map(wf => 
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; display:flex; justify-content:space-between; align-items:center; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.05)'" onmouseout="this.style.boxShadow='none'">
            <div>
                <div style="font-weight:600; font-size:1.05rem; color:#0f172a; margin-bottom:4px;"></div>
                <div style="font-size:0.8rem; color:#64748b; display:flex; gap:12px; align-items:center;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <div onclick="event.stopPropagation(); toggleWorkflowStatus(, '')" style="width:36px; height:20px; border-radius:10px; position:relative; cursor:pointer; transition:background-color 0.2s; background:;">
                            <div style="width:16px; height:16px; border-radius:50%; background:white; position:absolute; top:2px; transition:left 0.2s; left:; box-shadow:0 1px 2px rgba(0,0,0,0.1);"></div>
                        </div>
                        <span style="font-weight:600; color:; text-transform:capitalize;"></span>
                    </div>
                    <span>ID: </span>
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <button onclick="openWorkflowEditor()" style="padding:6px 14px; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Edit</button>
                <button onclick="deleteWorkflow()" style="padding:6px 14px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Delete</button>
            </div>
        </div>
    ).join('');
}
"""

if "window.renderWorkflowsList = function()" not in js:
    js += render_func
    print("Added window.renderWorkflowsList")
else:
    print("window.renderWorkflowsList already exists")

# 3. Update toggleWorkflowStatus to be optimistic
old_toggle = """window.toggleWorkflowStatus = async function(wfId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    try {
        const res = await authFetch(/api/workflows//status, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update status');
        loadWorkflowsView(); // Refresh the view
    } catch (err) {
        alert('Failed to toggle workflow status: ' + err.message);
    }
}"""

new_toggle = """window.toggleWorkflowStatus = async function(wfId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    
    // Optimistic UI Update
    if (window.currentWorkflows) {
        const wf = window.currentWorkflows.find(w => w.id === wfId);
        if (wf) {
            wf.status = newStatus;
            window.renderWorkflowsList();
        }
    }

    try {
        const res = await authFetch(/api/workflows//status, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update status');
    } catch (err) {
        alert('Failed to toggle workflow status: ' + err.message);
        // Revert Optimistic Update
        if (window.currentWorkflows) {
            const wf = window.currentWorkflows.find(w => w.id === wfId);
            if (wf) {
                wf.status = currentStatus;
                window.renderWorkflowsList();
            }
        }
    }
}"""

if old_toggle in js:
    js = js.replace(old_toggle, new_toggle)
    print("Replaced toggleWorkflowStatus with optimistic version.")
else:
    # try regex replacement
    import re
    pattern = re.compile(r'window\.toggleWorkflowStatus = async function.*?\}', re.DOTALL)
    if pattern.search(js):
        js = pattern.sub(new_toggle, js)
        print("Regex replaced toggleWorkflowStatus")
    else:
        print("WARNING: Could not find toggleWorkflowStatus")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
