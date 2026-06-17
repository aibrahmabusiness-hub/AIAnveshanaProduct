import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace multiple loadWorkflowsView, loadFlowsPage, renderFlowsTable
content = re.sub(r'async function loadWorkflowsView.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'async function loadFlowsPage.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'function renderFlowsTable.*?\}', '', content, flags=re.DOTALL)

new_code = '''
async function loadWorkflowsView() {
    const list = document.getElementById('workflowsList');
    if (!list) return;

    list.innerHTML = <div style="text-align:center; padding:40px; color:#94a3b8;"><div style="width:32px;height:32px;border:3px solid #e2e8f0;border-top-color:#6366f1;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 12px;"></div>Loading workflows...</div>;

    try {
        const res = await authFetch('/api/workflows');
        const data = await res.json();
        
        const workflows = data.workflows || [];
        
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
                    <div style="font-size:0.8rem; color:#64748b; display:flex; gap:12px;">
                        <span><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:; margin-right:6px;"></span></span>
                        <span>ID: </span>
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button onclick="openWorkflowEditor()" style="padding:6px 14px; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Edit</button>
                    <button onclick="deleteWorkflow()" style="padding:6px 14px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.85rem;">Delete</button>
                </div>
            </div>
        ).join('');
    } catch (err) {
        console.error('Failed to load workflows:', err);
        list.innerHTML = <div style="color:#ef4444; padding:20px; background:#fef2f2; border:1px solid #fecaca; border-radius:8px;">Failed to load workflows: </div>;
    }
}
'''

content += '\\n' + new_code

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
