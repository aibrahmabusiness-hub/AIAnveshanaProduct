const canvasLogic = `
// ==========================================
// Custom Canvas Drag & Drop Logic
// ==========================================
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
        node.innerHTML = \`
            <div class="node-icon" style="background:#f1f5f9; color:#475569;">\${iconChar}</div>
            <div class="node-title">\${displayName}</div>
        \`;
        
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
    
    // Need a global dragover to allow dropping anywhere in the canvas
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
        
        // Since the node is translated -50% -50%, we set left/top to the mouse position 
        // adjusted by the offset relative to the center.
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
    const nodeId = nodeElement.dataset.id;
    let displayName = nodeType;
    if (typeof availablePieces !== 'undefined') {
        const piece = availablePieces.find(p => p.name === nodeType);
        if (piece) displayName = piece.displayName;
    }
    
    modal.innerHTML = \`
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h3 style="margin:0; font-size:1.1rem; color:#0f172a;">\${displayName} Settings</h3>
            <button onclick="document.getElementById('stepSettingsModal').style.display='none'" style="background:none; border:none; font-size:1.2rem; cursor:pointer; color:#64748b;">&times;</button>
        </div>
        <div style="margin-bottom:12px;">
            <label style="display:block; font-size:0.8rem; font-weight:600; color:#475569; margin-bottom:4px;">Node Name</label>
            <input type="text" id="stepNameInput" value="\${nodeElement.querySelector('.node-title').textContent}" style="width:100%; padding:8px; border:1px solid #e2e8f0; border-radius:6px;">
        </div>
        <div style="margin-bottom:12px;">
            <label style="display:block; font-size:0.8rem; font-weight:600; color:#475569; margin-bottom:4px;">Action / Configuration</label>
            <select style="width:100%; padding:8px; border:1px solid #e2e8f0; border-radius:6px; margin-bottom:10px;">
                <option>Select an action...</option>
            </select>
            <textarea placeholder="Type @ to reference variables" style="width:100%; height:80px; padding:8px; border:1px solid #e2e8f0; border-radius:6px; font-family:monospace; font-size:0.85rem; resize:vertical;"></textarea>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:20px;">
            <button onclick="this.closest('#stepSettingsModal')._targetNode.remove(); this.closest('#stepSettingsModal').style.display='none';" style="padding:8px 16px; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:6px; cursor:pointer;">Delete Step</button>
            <button onclick="document.getElementById('stepSettingsModal').style.display='none'" class="btn-primary" style="padding:8px 16px; border-radius:6px; cursor:pointer;">Save</button>
        </div>
    \`;
    modal._targetNode = nodeElement;
    
    // Add event listener to update node title when input changes
    document.getElementById('stepNameInput').addEventListener('input', (e) => {
        nodeElement.querySelector('.node-title').textContent = e.target.value;
    });
}
`;

const fs = require('fs');
let content = fs.readFileSync('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'utf8');
if (!content.includes('Custom Canvas Drag & Drop Logic')) {
    content += '\n' + canvasLogic;
    
    if (content.includes('loadPieces();') && !content.includes('initCustomCanvas();')) {
        content = content.replace('loadPieces();', 'loadPieces();\n    initCustomCanvas();');
    }
    
    fs.writeFileSync('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', content, 'utf8');
}
