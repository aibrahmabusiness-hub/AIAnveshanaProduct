import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

new_func = """function showInspector(nodeId) {
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
        
        <!-- Tabs -->
        <div style="display:flex; border-bottom:1px solid #e2e8f0; margin-bottom:16px;">
            <div id="tab-parameters" style="padding:8px 16px; cursor:pointer; font-weight:600; color:#4f46e5; border-bottom:2px solid #4f46e5;" onclick="switchNodeTab('parameters')">Parameters</div>
            <div id="tab-testnode" style="padding:8px 16px; cursor:pointer; font-weight:600; color:#64748b;" onclick="switchNodeTab('testnode')">Test Step</div>
        </div>

        <div id="tab-content-parameters">
            <div id="nodeInspectParams"></div>
        </div>
        
        <div id="tab-content-testnode" style="display:none;">
            <button class="btn" style="width:100%; padding:8px 16px; background:#3b82f6; color:white; border:none; border-radius:8px; font-weight:600; cursor:pointer; margin-bottom:12px;" id="testNodeBtn" onclick="testCurrentNode()">? Test Step</button>
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px; font-weight:600;">OUTPUT DATA</div>
            <pre id="testNodeOutput" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; font-size:0.8rem; color:#334155; overflow-x:auto; min-height:100px;">Run the step to see output.</pre>
        </div>
    `;

    const paramsContainer = document.getElementById('nodeInspectParams');

    // Upstream outputs
    const upstreamOutputs = workflowSteps.slice(0, stepIndex).map(s => {
        return `<code style="background:#fef3c7;padding:2px 5px;border-radius:3px;margin:2px;display:inline-block;cursor:pointer;color:#d97706;border:1px solid #fde68a;" onclick="navigator.clipboard.writeText('{{${s.id}}}')" title="Click to copy ${s.type} output">{{${s.id}}}</code>`;
    }).filter(Boolean);

    // Show available variables as hints
    if (upstreamOutputs.length > 0 && !step.type.startsWith('trigger')) {
        const hint = document.createElement('div');
        hint.style.cssText = 'background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;padding:8px 10px;margin-bottom:12px;font-size:0.72rem;';
        let hintHtml = '';
        if (upstreamOutputs.length > 0) {
            hintHtml += `<div style="font-weight:700;color:#0369a1;margin-bottom:4px;">?? Upstream Outputs</div>` + upstreamOutputs.join('');
        }
        hint.innerHTML = hintHtml;
        paramsContainer.appendChild(hint);
    }

    if (schema.props) {
        Object.keys(schema.props).forEach(key => {
            const prop = schema.props[key];
            const div = document.createElement('div');
            div.style.marginBottom = '12px';
            const label = document.createElement('label');
            label.textContent = prop.displayName + (prop.required ? ' *' : '');
            label.style.display = 'block';
            label.style.fontSize = '0.8rem';
            label.style.fontWeight = '600';
            label.style.color = '#334155';
            label.style.marginBottom = '4px';
            div.appendChild(label);
            
            const input = buildParamInput(key, prop, step);
            div.appendChild(input);

            if (prop.description) {
                const desc = document.createElement('div');
                desc.textContent = prop.description;
                desc.style.fontSize = '0.7rem';
                desc.style.color = '#94a3b8';
                desc.style.marginTop = '2px';
                div.appendChild(desc);
            }
            paramsContainer.appendChild(div);
        });
    }
}

window.switchNodeTab = function(tabName) {
    const tabParams = document.getElementById('tab-parameters');
    const tabTest = document.getElementById('tab-testnode');
    const contentParams = document.getElementById('tab-content-parameters');
    const contentTest = document.getElementById('tab-content-testnode');
    if(!tabParams) return;
    
    if (tabName === 'parameters') {
        tabParams.style.borderBottom = '2px solid #4f46e5';
        tabParams.style.color = '#4f46e5';
        tabTest.style.borderBottom = 'none';
        tabTest.style.color = '#64748b';
        contentParams.style.display = 'block';
        contentTest.style.display = 'none';
    } else {
        tabTest.style.borderBottom = '2px solid #4f46e5';
        tabTest.style.color = '#4f46e5';
        tabParams.style.borderBottom = 'none';
        tabParams.style.color = '#64748b';
        contentParams.style.display = 'none';
        contentTest.style.display = 'block';
    }
}
"""

js = re.sub(r'function showInspector\(nodeId\).*?(?=\nfunction saveWorkflow)', new_func, js, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
