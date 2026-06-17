import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the HTML generation in loadToolsView
old_html_gen = """        html += `
            <div class="tools-group-card">
                <div class="tools-group-header">
                    <div class="tools-group-title" style="display: flex; align-items: center; gap: 12px;">
                        ${getAppIconMarkup(group.id)}
                        <strong style="font-size:1.1rem; color:#0f172a;">${group.name}</strong>
                    </div>
                    <span class="${statusBadgeClass}">${statusText}</span>
                </div>
                ${!isConnected ? `
                    <div style="background:#fef2f2; border:1px solid #fca5a5; color:#b91c1c; font-size:0.8rem; padding:8px 12px; border-radius:6px; margin-bottom:12px;">
                        ⚠️ This integration is not connected. Configure credentials under <strong>Settings</strong> to enable these capabilities.
                    </div>
                ` : ''}
                <div class="tools-capabilities-grid">
                    ${groupTools.map(tool => {
                        const isChecked = connected.includes(tool.id) ? 'checked' : '';
                        const isDisabled = !isConnected ? 'disabled' : '';
                        return `
                            <div class="tools-capability-card" style="${!isConnected ? 'opacity: 0.6; cursor: not-allowed;' : ''}">
                                <input type="checkbox" class="tools-capability-checkbox" name="agentTools" value="${tool.id}" ${isChecked} ${isDisabled}>
                                <div class="tools-capability-info">
                                    <span class="tools-capability-name">${tool.name}</span>
                                    <span class="tools-capability-desc">${tool.description}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;"""

new_html_gen = """        html += `
            <div class="tools-group-card">
                <div class="tools-group-header" onclick="toggleToolsBody('${group.id}')" style="cursor:pointer;">
                    <div class="tools-group-title" style="display: flex; align-items: center; gap: 12px;">
                        ${getAppIconMarkup(group.id)}
                        <strong style="font-size:1.1rem; color:#0f172a;">${group.name}</strong>
                    </div>
                    <div style="display:flex; align-items:center; gap: 12px;">
                        <span class="${statusBadgeClass}">${statusText}</span>
                        <svg id="chevron-${group.id}" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.3s; color: #64748b;">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </div>
                </div>
                
                <div id="tools-body-${group.id}" style="display: none; padding-top: 16px; border-top: 1px solid #f1f5f9; margin-top: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="font-size:0.85rem; color:var(--text-muted);">
                            ${!isConnected ? 'Connect your account to enable these tools for the agent.' : 'Manage your connection settings.'}
                        </div>
                        ${!group.systemDefault ? `
                            <button onclick="openManageConnectionsModal('${group.id}')" style="background:var(--primary-color); color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:0.8rem; font-weight:600;">
                                ${isConnected ? 'Manage Connection' : 'Connect Account'}
                            </button>
                        ` : ''}
                    </div>
                    
                    <div class="tools-capabilities-grid">
                        ${groupTools.map(tool => {
                            const isChecked = connected.includes(tool.id) ? 'checked' : '';
                            const isDisabled = !isConnected ? 'disabled' : '';
                            return `
                                <div class="tools-capability-card" style="${!isConnected ? 'opacity: 0.6; cursor: not-allowed;' : ''}">
                                    <input type="checkbox" class="tools-capability-checkbox" name="agentTools" value="${tool.id}" ${isChecked} ${isDisabled}>
                                    <div class="tools-capability-info">
                                        <span class="tools-capability-name">${tool.name}</span>
                                        <span class="tools-capability-desc">${tool.description}</span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;"""

if old_html_gen in content:
    content = content.replace(old_html_gen, new_html_gen)
else:
    print("Could not find old HTML generation block.")

# Add toggleToolsBody function if not exists
toggle_func = """
window.toggleToolsBody = function(id) {
    const body = document.getElementById(`tools-body-${id}`);
    const chevron = document.getElementById(`chevron-${id}`);
    if (body.style.display === 'none') {
        body.style.display = 'block';
        if (chevron) chevron.style.transform = 'rotate(180deg)';
    } else {
        body.style.display = 'none';
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    }
};
"""

if "window.toggleToolsBody" not in content:
    content += toggle_func

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched project.js successfully")
