import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Replace the dot status indicator with a toggle switch
old_status_html = """                        <span><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:; margin-right:6px;"></span></span>"""

new_status_html = """                        <div style="display:flex; align-items:center; gap:6px;">
                            <div onclick="toggleWorkflowStatus(, '')" style="width:36px; height:20px; border-radius:10px; position:relative; cursor:pointer; transition:background-color 0.2s; background:;">
                                <div style="width:16px; height:16px; border-radius:50%; background:white; position:absolute; top:2px; transition:left 0.2s; left:; box-shadow:0 1px 2px rgba(0,0,0,0.1);"></div>
                            </div>
                            <span style="font-weight:600; color:; text-transform:capitalize;"></span>
                        </div>"""

if old_status_html in js:
    js = js.replace(old_status_html, new_status_html)
    print("Replaced status html with toggle switch.")
else:
    print("Could not find old_status_html in project.js")

# Add toggleWorkflowStatus function if it doesn't exist
toggle_func = """
window.toggleWorkflowStatus = async function(wfId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    try {
        const res = await authFetch(/api/workflows//status, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update status');
        loadWorkflowsView(); // Refresh the view
    } catch (err) {
        alert('Failed to toggle workflow status: ' + err.message);
    }
}
"""

if "window.toggleWorkflowStatus" not in js:
    js += "\n" + toggle_func
    print("Added toggleWorkflowStatus function.")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
