import re
with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Change const to let for NODE_SCHEMAS
js = js.replace("const NODE_SCHEMAS = {", "let NODE_SCHEMAS = {")

# 2. Add loadPieces function before initCustomCanvas
load_pieces_func = """
let availablePieces = [];
async function loadPieces() {
    try {
        const res = await authFetch('/api/pieces');
        if (res.ok) {
            const data = await res.json();
            availablePieces = data.pieces || [];
            populateToolbox();
        }
    } catch (err) {
        console.error('Failed to load pieces', err);
    }
}

function populateToolbox() {
    const toolbox = document.getElementById('dynamic-toolbox');
    if (!toolbox) return;
    
    let html = '';
    
    // Always add triggers
    html += `
    <div style="font-size:0.75rem; font-weight:600; color:#94a3b8; margin-bottom:4px; text-transform:uppercase;">Triggers</div>
    <div class="toolbox-item" draggable="true" data-node="trigger_manual">
        <div class="toolbox-item-icon" style="background:#e2e8f0; color:#475569;">M</div>
        <div class="toolbox-item-info">
            <span class="toolbox-item-name">Manual Trigger</span>
        </div>
    </div>`;
    
    // Add Activepieces
    availablePieces.forEach(p => {
        if (!p.actions || p.actions.length === 0) return;
        html += `<div style="font-size:0.75rem; font-weight:600; color:#94a3b8; margin-bottom:4px; margin-top:12px; text-transform:uppercase;">${p.displayName}</div>`;
        p.actions.forEach(a => {
            const nodeKey = `${p.name}::${a.name}`;
            
            // Add to schema
            NODE_SCHEMAS[nodeKey] = {
                name: a.displayName,
                icon: p.displayName.charAt(0),
                desc: a.description,
                params: Object.keys(a.props || {}).map(k => {
                    const prop = a.props[k];
                    return {
                        name: k,
                        label: prop.displayName,
                        placeholder: prop.description || '',
                        type: prop.type
                    };
                })
            };
            
            html += `
            <div class="toolbox-item" draggable="true" data-node="${nodeKey}">
                <div class="toolbox-item-icon" style="background:#e0e7ff; color:#4f46e5;">
                    <img src="${p.logoUrl}" style="width:16px; height:16px;" onerror="this.style.display='none'">
                </div>
                <div class="toolbox-item-info">
                    <span class="toolbox-item-name">${a.displayName}</span>
                    <span class="toolbox-item-desc" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${a.description || ''}</span>
                </div>
            </div>`;
        });
    });
    
    toolbox.innerHTML = html;
    
    // Re-bind drag events for toolbox items
    document.querySelectorAll('#dynamic-toolbox .toolbox-item').forEach(item => {
        item.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', 'TOOLBOX:' + item.dataset.node);
            e.dataTransfer.effectAllowed = 'copy';
        });
    });
}
"""

js = js.replace("function initCustomCanvas() {", load_pieces_func + "\nfunction initCustomCanvas() {\n    loadPieces();")

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
