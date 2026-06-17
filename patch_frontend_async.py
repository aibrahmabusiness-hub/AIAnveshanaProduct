import os
import re

file_js = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
file_css = r"c:\Users\Admin\Documents\Agentic AI\frontend\style.css"

with open(file_js, "r", encoding="utf-8") as f:
    js_content = f.read()

# 1. Update loadKnowledgeBase
old_render = """    docsList.innerHTML = data.documents.map(doc => `
        <div class="kb-doc-row">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            <span>${doc.filename}</span>
            <div style="display:flex; gap:8px;">
                <button class="icon-btn" onclick="deleteKnowledgeDoc(${doc.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        </div>
    `).join('');"""

new_render = """    let isProcessing = false;
    docsList.innerHTML = data.documents.map(doc => {
        let statusBadge = '';
        if (doc.sync_status === 'processing') {
            isProcessing = true;
            statusBadge = `<span class="status-badge processing"><span class="spinner-mini"></span> In Progress</span>`;
        } else if (doc.sync_status === 'synced') {
            statusBadge = `<span class="status-badge synced">Synced</span>`;
        } else if (doc.sync_status === 'failed') {
            statusBadge = `<span class="status-badge failed">Failed</span>`;
        }
        
        let retryBtn = '';
        if (doc.sync_status === 'failed') {
            retryBtn = `<button class="btn-cancel" style="padding: 4px 8px; font-size: 0.7rem; margin-right: 8px;" onclick="retryKnowledgeSync(${doc.id})">Retry Sync</button>`;
        }

        return `
        <div class="kb-doc-row">
            <div style="display:flex; align-items:center; gap:8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--orange-primary)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                <span>${doc.filename}</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                ${statusBadge}
                ${retryBtn}
                <button class="icon-btn" onclick="deleteKnowledgeDoc(${doc.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        </div>
        `;
    }).join('');
    
    // Auto polling if any document is processing
    if (window._kbPollTimer) clearTimeout(window._kbPollTimer);
    if (isProcessing) {
        window._kbPollTimer = setTimeout(() => {
            if (document.getElementById('view-knowledge').classList.contains('active')) {
                loadKnowledgeBase();
            }
        }, 3000);
    }"""

js_content = js_content.replace(old_render, new_render)

# Add retryKnowledgeSync
if "async function retryKnowledgeSync" not in js_content:
    js_content += """

async function retryKnowledgeSync(docId) {
    try {
        const res = await authFetch(`/api/knowledge/${agentId}/sync/${docId}`, { method: 'POST' });
        if (!res.ok) throw new Error('Failed to retry sync');
        loadKnowledgeBase();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}
"""

with open(file_js, "w", encoding="utf-8") as f:
    f.write(js_content)


# Update style.css
with open(file_css, "r", encoding="utf-8") as f:
    css_content = f.read()

if ".status-badge" not in css_content:
    css_content += """
/* Status Badges */
.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.status-badge.processing {
    background: #fffbeb;
    color: #d97706;
    border: 1px solid #fde68a;
}
.status-badge.synced {
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
}
.status-badge.failed {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
}

.spinner-mini {
    width: 10px;
    height: 10px;
    border: 2px solid currentColor;
    border-bottom-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Ensure kb-doc-row aligns nicely */
.kb-doc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 8px;
}
"""

with open(file_css, "w", encoding="utf-8") as f:
    f.write(css_content)

print("Patched frontend successfully.")
