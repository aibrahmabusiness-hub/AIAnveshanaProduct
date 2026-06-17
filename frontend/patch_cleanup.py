import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\frontend\project.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace createNewWorkflow
create_new_wf_old = r"async function createNewWorkflow\(\) \{.*?\n\}"
create_new_wf_new = """async function createNewWorkflow() {
    document.getElementById('workflowModal').classList.add('active');
    currentFlowId = null;
    const frame = document.getElementById('react-flow-frame');
    if (frame) {
        frame.src = `/v2-canvas?id=new_workflow&agent_id=${agentId}`;
    }
}"""
content = re.sub(create_new_wf_old, create_new_wf_new, content, flags=re.DOTALL)

# Replace openWorkflowEditor
open_wf_old = r"async function openWorkflowEditor\(flowId = null\) \{.*?\n\}"
open_wf_new = """async function openWorkflowEditor(flowId = null) {
    if (!flowId) {
        createNewWorkflow();
        return;
    }
    document.getElementById('workflowModal').classList.add('active');
    currentFlowId = flowId;
    const frame = document.getElementById('react-flow-frame');
    if (frame) {
        frame.src = `/v2-canvas?id=${currentFlowId}&agent_id=${agentId}`;
    }
}"""
content = re.sub(open_wf_old, open_wf_new, content, flags=re.DOTALL)

# Fix V2 Canvas fetch error
v2_filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(v2_filepath, 'r', encoding='utf-8') as f:
    v2_content = f.read()

v2_content = v2_content.replace("const id = urlParams.get('id') || 'wf-live';", "const id = urlParams.get('id') || 'new_workflow';")

with open(v2_filepath, 'w', encoding='utf-8') as f:
    f.write(v2_content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
