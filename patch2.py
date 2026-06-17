import re
with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

new_build_param = """function buildParamInput(nodeId, paramDef, value) {
    const wrap = document.createElement('div');
    wrap.style.marginBottom = '12px';
    const label = document.createElement('label');
    label.textContent = paramDef.label;
    label.style.cssText = 'display:block;font-size:0.75rem;font-weight:600;color:var(--text-secondary);margin-bottom:4px;';
    wrap.appendChild(label);

    let input;
    if (paramDef.type === 'LONG_TEXT' || paramDef.type === 'textarea') {
        input = document.createElement('textarea');
        input.style.cssText = 'width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;font-size:0.85rem;background:var(--bg-primary);color:var(--text-primary);resize:vertical;min-height:80px;';
    } else if (paramDef.type === 'STATIC_DROPDOWN' || paramDef.type === 'DROPDOWN' || paramDef.type === 'select') {
        input = document.createElement('select');
        input.style.cssText = 'width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;font-size:0.85rem;background:var(--bg-primary);color:var(--text-primary);';
        const defaultOpt = document.createElement('option');
        defaultOpt.value = ""; defaultOpt.textContent = "Select...";
        input.appendChild(defaultOpt);
        
        if (paramDef.options && paramDef.options.length) {
            paramDef.options.forEach(opt => {
                const o = document.createElement('option');
                if (typeof opt === 'string') { o.value = opt; o.textContent = opt; }
                else { o.value = opt.value; o.textContent = opt.label; }
                input.appendChild(o);
            });
        }
    } else if (paramDef.type === 'CHECKBOX') {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.style.marginRight = '8px';
        wrap.insertBefore(input, label);
        wrap.style.display = 'flex';
        wrap.style.flexDirection = 'row-reverse';
        wrap.style.justifyContent = 'flex-end';
        wrap.style.alignItems = 'center';
    } else if (paramDef.type === 'NUMBER') {
        input = document.createElement('input');
        input.type = 'number';
        input.style.cssText = 'width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;font-size:0.85rem;background:var(--bg-primary);color:var(--text-primary);';
    } else {
        input = document.createElement('input');
        input.type = 'text';
        input.style.cssText = 'width:100%;padding:8px;border:1px solid var(--border-color);border-radius:6px;font-size:0.85rem;background:var(--bg-primary);color:var(--text-primary);';
    }
    
    if (paramDef.type !== 'CHECKBOX' && paramDef.placeholder) input.placeholder = paramDef.placeholder;
    if (paramDef.type === 'CHECKBOX') {
        input.checked = value === true || value === 'true';
    } else {
        input.value = value || '';
    }
    
    input.addEventListener('change', (e) => {
        const stepIndex = workflowSteps.findIndex(s => s.id === nodeId);
        if (stepIndex > -1) {
            let val = paramDef.type === 'CHECKBOX' ? e.target.checked : e.target.value;
            workflowSteps[stepIndex].data[paramDef.name] = val;
        }
    });

    if (paramDef.type !== 'CHECKBOX') wrap.appendChild(input);
    return wrap;
}"""

# Replace the old buildParamInput
js = re.sub(r'function buildParamInput\(nodeId, paramDef, value\) \{.*?(?=\nfunction getWorkflowVariables)', new_build_param + '\n', js, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
