import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any occurrence of html += \ with html += `
content = re.sub(r'html \+=\s*\\\n', r'html += `\n', content)
content = re.sub(r'html \+=\s*\\r\\n', r'html += `\n', content)

# Since PowerShell strips the closing backticks as well, I might have `";` instead of `\`;`
# Wait, `html += \` was probably `html += \`` ? No, powershell `\`` evaluates to a backtick.
# So wait! If I typed \` in powershell, it becomes ` in the output.
# If I typed \\` in powershell, it becomes \` in the output!
# Ah! In my PowerShell script I had: `html += \``
# This resulted in `html += \` (backslash and backtick) or something?
# Let's just fix it completely using python block replacement.

# Let's find the loadPieces and populateToolbox functions and replace them entirely:

correct_code = """
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
"""

match = re.search(r'let availablePieces = \[\];.*?async function loadPieces\(\)', content)
if match:
    # Just replace from loadPieces onwards until the end of populateToolbox
    # The end of populateToolbox is the "});\n}"
    end_match = re.search(r'\}\);\n\}', content[match.start():])
    if end_match:
        start_idx = match.start()
        end_idx = start_idx + end_match.end()
        content = content[:start_idx] + correct_code + content[end_idx:]

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
