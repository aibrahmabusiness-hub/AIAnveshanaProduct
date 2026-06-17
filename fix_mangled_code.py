import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the mangled createNewWorkflow function
match = re.search(r'function createNewWorkflow\(\) \{', content)
if match:
    # Delete everything from function createNewWorkflow() to the end of the file
    content = content[:match.start()]

fixed_code = '''
function createNewWorkflow() {
    currentFlow = null;
    document.getElementById('workflowModal').classList.add('active');
    document.getElementById('workflowNameInput').value = 'Untitled Workflow';
    
    // Clear canvas
    document.getElementById('custom-canvas').innerHTML = '';
    
    // Create start node
    const startNode = document.createElement('div');
    startNode.className = 'canvas-node';
    startNode.dataset.id = 'trigger';
    startNode.style.left = '50%';
    startNode.style.top = '50px';
    startNode.style.transform = 'translateX(-50%)';
    startNode.innerHTML = `
        <div class="node-icon" style="background:#f1f5f9; color:#475569;">T</div>
        <div class="node-title">Trigger</div>
    `;
    
    document.getElementById('custom-canvas').appendChild(startNode);
}

function openWorkflowEditor(flowId = null) {
    if (!flowId) {
        createNewWorkflow();
        return;
    }
    document.getElementById('workflowModal').classList.add('active');
    // In a full implementation, we'd load the flow data and render the nodes
}

function closeWorkflowEditor() {
    document.getElementById('workflowModal').classList.remove('active');
}

async function deleteWorkflow(id) {
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    try {
        const res = await authFetch(`/api/workflows/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete workflow');
        loadWorkflowsView();
    } catch (err) {
        alert(err.message);
    }
}
'''

content += fixed_code

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
