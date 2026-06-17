with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

code_to_append = """
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
        const toolbox = document.getElementById('dynamic-toolbox');
        if (toolbox) {
            toolbox.innerHTML = '<div style="color:red; padding:10px;">Failed to load apps</div>';
        }
    }
}

function populateToolbox() {
    const toolbox = document.getElementById('dynamic-toolbox');
    if (!toolbox) return;
    
    let html = '';
    
    // Always add manual trigger
    html += `
    <div style="font-size:0.75rem; font-weight:600; color:#94a3b8; margin-bottom:4px; text-transform:uppercase;">Triggers</div>
    <div class="toolbox-item" draggable="true" data-node="trigger_manual">
        <div class="toolbox-item-icon" style="background:#e2e8f0; color:#475569;">M</div>
        <div class="toolbox-item-info">
            <div class="toolbox-item-title">Manual Trigger</div>
            <div class="toolbox-item-desc">Trigger from UI</div>
        </div>
    </div>
    <div class="toolbox-item" draggable="true" data-node="trigger_webhook">
        <div class="toolbox-item-icon" style="background:#e2e8f0; color:#475569;">W</div>
        <div class="toolbox-item-info">
            <div class="toolbox-item-title">Webhook</div>
            <div class="toolbox-item-desc">Trigger via URL</div>
        </div>
    </div>
    `;
    
    html += '<div style="font-size:0.75rem; font-weight:600; color:#94a3b8; margin-top:16px; margin-bottom:4px; text-transform:uppercase;">Apps</div>';
    
    if (availablePieces.length === 0) {
        html += '<div style="font-size:0.8rem; color:#64748b;">No apps installed.</div>';
    } else {
        availablePieces.forEach(p => {
            html += `
            <div class="toolbox-item" draggable="true" data-node="${p.name}">
                <div class="toolbox-item-icon" style="background:#f1f5f9; color:#475569;">${p.displayName.charAt(0).toUpperCase()}</div>
                <div class="toolbox-item-info">
                    <div class="toolbox-item-title">${p.displayName}</div>
                    <div class="toolbox-item-desc">${p.description || p.name}</div>
                </div>
            </div>
            `;
        });
    }
    
    toolbox.innerHTML = html;
    
    // Re-bind drag events for toolbox items
    document.querySelectorAll('#dynamic-toolbox .toolbox-item').forEach(item => {
        item.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', 'TOOLBOX:' + item.dataset.node);
            e.dataTransfer.effectAllowed = 'copy';
        });
    });
}

function initCustomCanvas() {
    const canvas = document.getElementById('custom-canvas');
    if (!canvas) return;

    canvas.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        canvas.style.background = '#f8fafc';
    });

    canvas.addEventListener('dragleave', e => {
        e.preventDefault();
        canvas.style.background = '#fff';
    });

    canvas.addEventListener('drop', e => {
        e.preventDefault();
        canvas.style.background = '#fff';
        
        const data = e.dataTransfer.getData('text/plain');
        if (!data || !data.startsWith('TOOLBOX:')) return;
        
        const nodeType = data.split(':')[1];
        
        // Find the piece info if available
        let displayName = nodeType;
        let iconChar = nodeType.charAt(0).toUpperCase();
        
        if (nodeType.startsWith('trigger_')) {
            displayName = nodeType === 'trigger_manual' ? 'Manual Trigger' : 'Webhook';
            iconChar = nodeType === 'trigger_manual' ? 'M' : 'W';
        } else if (typeof availablePieces !== 'undefined') {
            const piece = availablePieces.find(p => p.name === nodeType);
            if (piece) {
                displayName = piece.displayName;
                iconChar = displayName.charAt(0).toUpperCase();
            }
        }
        
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const node = document.createElement('div');
        node.className = 'canvas-node';
        node.dataset.id = nodeType + '_' + Date.now();
        node.dataset.type = nodeType;
        node.style.left = x + 'px';
        node.style.top = y + 'px';
        node.style.transform = 'translate(-50%, -50%)';
        node.innerHTML = `
            <div class="node-icon" style="background:#f1f5f9; color:#475569;">${iconChar}</div>
            <div class="node-title">${displayName}</div>
        `;
        
        // Make it draggable
        node.draggable = true;
        node.addEventListener('dragstart', dragStartNode);
        
        // Add click for settings
        node.addEventListener('click', (e) => {
            e.stopPropagation();
            openStepSettings(node);
        });
        
        canvas.appendChild(node);
    });
    
    // Add click event on canvas to deselect/close settings
    canvas.addEventListener('click', () => {
        const modal = document.getElementById('stepSettingsModal');
        if (modal) modal.style.display = 'none';
    });
}

let draggedNode = null;
let dragOffsetX = 0;
let dragOffsetY = 0;

function dragStartNode(e) {
    draggedNode = e.target.closest('.canvas-node');
    if (!draggedNode) return;
    
    // Calculate offset so we don't snap the node center to the mouse
    const rect = draggedNode.getBoundingClientRect();
    dragOffsetX = e.clientX - rect.left;
    dragOffsetY = e.clientY - rect.top;
    
    e.dataTransfer.setData('text/plain', 'NODE_DRAG');
    e.dataTransfer.effectAllowed = 'move';
    
    document.addEventListener('dragover', globalDragOver);
    document.addEventListener('drop', globalDrop);
}

function globalDragOver(e) {
    if (!draggedNode) return;
    e.preventDefault();
}

function globalDrop(e) {
    if (!draggedNode) return;
    e.preventDefault();
    
    const canvas = document.getElementById('custom-canvas');
    if (e.target.closest('#custom-canvas')) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        draggedNode.style.left = x + 'px';
        draggedNode.style.top = y + 'px';
    }
    
    document.removeEventListener('dragover', globalDragOver);
    document.removeEventListener('drop', globalDrop);
    draggedNode = null;
}

function openStepSettings(nodeElement) {
    let modal = document.getElementById('stepSettingsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'stepSettingsModal';
        modal.style.cssText = 'position:absolute; right:20px; top:20px; width:350px; background:white; border:1px solid #e2e8f0; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.1); padding:20px; z-index:100;';
        document.getElementById('workflowModal').appendChild(modal);
    }
    
    modal.style.display = 'block';
    
    const nodeType = nodeElement.dataset.type;
    let displayName = nodeType;
    if (typeof availablePieces !== 'undefined') {
        const piece = availablePieces.find(p => p.name === nodeType);
        if (piece) displayName = piece.displayName;
    }
    
    modal.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h3 style="margin:0; font-size:1.1rem; color:#0f172a;">${displayName} Settings</h3>
            <button onclick="document.getElementById('stepSettingsModal').style.display='none'" style="background:none; border:none; font-size:1.2rem; cursor:pointer; color:#64748b;">&times;</button>
        </div>
        <div style="margin-bottom:12px;">
            <label style="display:block; font-size:0.8rem; font-weight:600; color:#475569; margin-bottom:4px;">Node Name</label>
            <input type="text" id="stepNameInput" value="${nodeElement.querySelector('.node-title').textContent}" style="width:100%; padding:8px; border:1px solid #e2e8f0; border-radius:6px;">
        </div>
        <div style="margin-bottom:12px;">
            <label style="display:block; font-size:0.8rem; font-weight:600; color:#475569; margin-bottom:4px;">Action / Configuration</label>
            <select style="width:100%; padding:8px; border:1px solid #e2e8f0; border-radius:6px; margin-bottom:10px;">
                <option>Select an action...</option>
            </select>
            <textarea placeholder="Type @ to reference variables" style="width:100%; height:80px; padding:8px; border:1px solid #e2e8f0; border-radius:6px; font-family:monospace; font-size:0.85rem; resize:vertical;"></textarea>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:20px;">
            <button onclick="document.getElementById('stepSettingsModal')._targetNode.remove(); document.getElementById('stepSettingsModal').style.display='none';" style="padding:8px 16px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer;">Delete Step</button>
            <button onclick="document.getElementById('stepSettingsModal').style.display='none'" class="btn-primary" style="padding:8px 16px; border-radius:6px; cursor:pointer;">Save</button>
        </div>
    `;
    modal._targetNode = nodeElement;
    
    // Add event listener to update node title when input changes
    document.getElementById('stepNameInput').addEventListener('input', (e) => {
        nodeElement.querySelector('.node-title').textContent = e.target.value;
    });
}
"""

if "let availablePieces" not in content:
    content += "\n" + code_to_append
    
    # ensure loadPieces and initCustomCanvas are called
    content = content.replace("document.getElementById('workflowModal').classList.add('active');", "document.getElementById('workflowModal').classList.add('active');\n    loadPieces();\n    initCustomCanvas();")
    
    with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
        f.write(content)
