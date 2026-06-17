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
    startNode.innerHTML = 
        <div class="node-icon" style="background:#f1f5f9; color:#475569;">T</div>
        <div class="node-title">Trigger</div>
    ;
    
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
