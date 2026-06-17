import re
with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

new_inspectors = """function hideInspector() {
    const panel = document.getElementById('step-properties-panel');
    if (panel) {
        panel.innerHTML = '<div style="text-align:center; color:#94a3b8; font-size:0.85rem; padding-top:40px;">Select a step to configure its properties.</div>';
    }
}

function showInspector(nodeId) {
    const stepIndex = workflowSteps.findIndex(s => s.id === nodeId);
    if (stepIndex === -1) return;
    const step = workflowSteps[stepIndex];
    const schema = NODE_SCHEMAS[step.type];
    if (!schema) return;

    const panel = document.getElementById('step-properties-panel');
    if (!panel) return;
    
    panel.innerHTML = `
        <div style="margin-bottom:16px;">
            <h4 id="nodeInspectTitle" style="margin:0; font-size:1.1rem; color:#0f172a;">${schema.name}</h4>
            <div id="nodeInspectType" style="font-size:0.75rem; color:#64748b; margin-top:2px;">${step.type}</div>
        </div>
        <div id="nodeInspectParams"></div>
    `;

    const paramsContainer = document.getElementById('nodeInspectParams');

    // Upstream outputs
    const upstreamOutputs = workflowSteps.slice(0, stepIndex).map(s => {
        return `<code style="background:#fef3c7;padding:2px 5px;border-radius:3px;margin:2px;display:inline-block;cursor:pointer;color:#d97706;border:1px solid #fde68a;" onclick="navigator.clipboard.writeText('{{${s.id}_output}}')" title="Click to copy ${s.type} output">{{${s.id}_output}}</code>`;
    }).filter(Boolean);

    // Show available variables as hints
    const vars = getWorkflowVariables();
    if ((vars.length > 0 || upstreamOutputs.length > 0) && step.type !== 'trigger_webhook' && step.type !== 'trigger_manual') {
        const hint = document.createElement('div');
        hint.style.cssText = 'background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;padding:8px 10px;margin-bottom:12px;font-size:0.72rem;';
        let hintHtml = '';
        if (vars.length > 0) {
            hintHtml += `<div style="font-weight:700;color:#0369a1;margin-bottom:4px;">?? Global Variables</div>` +
                vars.map(v => `<code style="background:#e0f2fe;padding:2px 5px;border-radius:3px;margin:2px;display:inline-block;cursor:pointer;" onclick="navigator.clipboard.writeText('{{${v.name}}}')" title="Click to copy">{{${v.name}}}</code>`).join('');
        }
        if (upstreamOutputs.length > 0) {
            hintHtml += `<div style="font-weight:700;color:#b45309;margin-top:6px;margin-bottom:4px;">?? Upstream Outputs</div>` + upstreamOutputs.join('');
        }
        hint.innerHTML = hintHtml;
        paramsContainer.appendChild(hint);
    }

    if (step.type === 'trigger_webhook') {
        const div = document.createElement('div');
        div.style.cssText = 'font-size:0.8rem;color:var(--text-secondary);line-height:1.5;';
        div.innerHTML = `<p><strong>Webhook URL:</strong></p>
            <code style="background:var(--bg-primary);padding:6px;border-radius:4px;font-family:monospace;display:block;margin:6px 0;border:1px solid var(--border-color);font-size:0.72rem;word-break:break-all;">${window.location.origin}/api/workflows/trigger</code>
            <p style="color:var(--text-muted);font-size:0.75rem;">POST JSON to this URL to start the workflow externally.</p>`;
        paramsContainer.appendChild(div);
    } else if (step.type === 'trigger_manual' || step.type === 'trigger_schedule') {
        const div = document.createElement('div');
        div.style.cssText = 'font-size:0.8rem;color:var(--text-muted);text-align:center;padding:12px 0;';
        div.textContent = step.type === 'trigger_schedule' ? 'Configure cron schedule:' : 'This trigger starts the workflow manually.';
        paramsContainer.appendChild(div);
        if (step.type === 'trigger_schedule') {
            const param = { name: 'cron', label: 'Cron Expression', placeholder: '0 9 * * * (Every day at 9 AM)' };
            paramsContainer.appendChild(buildParamInput(nodeId, param, step.data[param.name] || ''));
        }
    } else if (step.type === 'logic_if') {
        const param = { name: 'condition', label: 'Python Condition', placeholder: 'e.g. {{s1_output}} > 50' };
        paramsContainer.appendChild(buildParamInput(nodeId, param, step.data[param.name] || ''));
    } else if (step.type === 'logic_loop') {
        const param = { name: 'array_var', label: 'Array Variable', placeholder: 'e.g. {{s1_output}}' };
        paramsContainer.appendChild(buildParamInput(nodeId, param, step.data[param.name] || ''));
    } else {
        if (schema.params && schema.params.length > 0) {
            schema.params.forEach(p => {
                paramsContainer.appendChild(buildParamInput(nodeId, p, step.data[p.name]));
            });
        } else {
            const div = document.createElement('div');
            div.style.cssText = 'font-size:0.8rem;color:var(--text-muted);text-align:center;padding:12px 0;';
            div.textContent = 'No configuration needed.';
            paramsContainer.appendChild(div);
        }
    }
}"""

js = re.sub(r'function showInspector\(nodeId\) \{.*?(?=\nfunction buildParamInput)', new_inspectors + '\n', js, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
