import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace executeWorkflow
new_exec = """async function executeWorkflow() {
    if (!currentEditingWorkflowId) {
        alert("Please save the workflow first before debugging.");
        return;
    }
    document.getElementById('debugConsole').style.display = 'flex';
    const content = document.getElementById('debugConsoleContent');
    content.innerHTML = '<div style="color:#e2e8f0;">? Executing workflow in debug mode...</div>';
    
    try {
        const res = await authFetch(`/api/workflows/${currentEditingWorkflowId}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { debug_mode: true }, steps: workflowSteps })
        });
        const result = await res.json();
        
        content.innerHTML = '';
        if (result.logs && result.logs.length > 0) {
            result.logs.forEach((logItem, idx) => {
                const color = logItem.success ? '#4ade80' : (logItem.error ? '#f87171' : '#cbd5e1');
                const status = logItem.success ? 'Success' : (logItem.error ? 'Error' : 'Info');
                const outputStr = logItem.result ? JSON.stringify(logItem.result) : (logItem.error || logItem.info || '');
                content.innerHTML += `<div style="margin-bottom:8px; padding-bottom:8px; border-bottom:1px dashed #334155;">
                    <span style="color:${color};font-weight:bold;">[Step ${logItem.step}]</span><br>
                    <span style="color:#94a3b8;">Status: ${status}</span><br>
                    <span style="color:#cbd5e1; word-wrap:break-word;">Output: ${outputStr}</span>
                </div>`;
            });
        } else {
            content.innerHTML = '<div style="color:#e2e8f0;">No steps executed. Result: ' + JSON.stringify(result) + '</div>';
        }
    } catch(err) {
        content.innerHTML = `<div style="color:#f87171;">Error executing workflow: ${err.message}</div>`;
    }
}"""
js = re.sub(r'async function executeWorkflow\(\).*?content\.innerHTML = `<div style="color:#f87171;">Error executing workflow: \$\{err\.message\}</div>`;\s*\}\s*\}', new_exec, js, flags=re.DOTALL)


# Also in showInspector, we need to fix how it formats the type if the lightweight-engine returns name correctly.
# The current showInspector logic is: `<div id="nodeInspectType" style="font-size:0.75rem; color:#64748b; margin-top:2px;">${step.type}</div>`
# I will just leave this as is since step.type will now be correct e.g. "@activepieces/piece-gmail::send_email".

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
