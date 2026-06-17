import os
import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Remove old broken function
js = re.sub(r"function getAppIconMarkup\(appName\) \{.*?\}\n", "", js, flags=re.DOTALL)

# Re-add with actual backticks
icon_function = """
function getAppIconMarkup(appName) {
    if (!appName) return `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>`;
    const type = appName.replace('@activepieces/piece-', '').toLowerCase();
    if (type.includes('gmail')) {
        return `<svg viewBox="0 0 24 24" width="24" height="24"><path fill="#EA4335" d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L12 8.338l8.073-4.845c1.618-1.214 3.927-.059 3.927 1.964z"/><path fill="#34A853" d="M18.545 21h3.819C23.268 21 24 20.268 24 19.366V5.457c0-.58-.313-1.104-.813-1.404z"/><path fill="#FBBC05" d="M23.187 4.053C22.285 3.376 21.1 3.535 20.073 4.152L12 8.991l-8.073-4.84A1.636 1.636 0 0 0 .813 4.053c0 .58.313 1.104.813 1.404l6.545 4.91L12 13.25l3.829-2.883z"/><path fill="#4285F4" d="M0 5.457v13.909c0 .904.732 1.636 1.636 1.636h3.819V11.73z"/></svg>`;
    } else if (type.includes('jira')) {
        return `<svg viewBox="0 0 24 24" width="24" height="24"><path fill="#2684FF" d="M11.53 11.76a4.28 4.28 0 1 0-6.06 6.06L11.53 23.88a4.28 4.28 0 0 0 6.05-6.05z"/><path fill="#0052CC" d="M12.01 1.05a4.28 4.28 0 0 0-6.06 6.06L12.01 13.17a4.28 4.28 0 0 0 6.05-6.05z"/><path fill="#2684FF" d="M23.51 12.01a4.28 4.28 0 0 0-6.05-6.05l-6.06 6.05a4.28 4.28 0 0 0 6.05 6.06z"/></svg>`;
    } else if (type.includes('servicenow')) {
        return `<svg viewBox="0 0 24 24" width="24" height="24"><path fill="#81B5A1" d="M12 0L2.6 5.4v13.2L12 24l9.4-5.4V5.4L12 0zm0 21.6L4.2 17.1V8.1L12 3.6l7.8 4.5v9L12 21.6z"/></svg>`;
    } else if (type.includes('salesforce')) {
        return `<svg viewBox="0 0 24 24" width="24" height="24"><path fill="#00A1E0" d="M15.82 4.1a3.63 3.63 0 0 0-3.1 1.77 4.52 4.52 0 0 0-6.72 1.83 2.91 2.91 0 0 0-2.52 2.87 2.85 2.85 0 0 0 2.85 2.85h9.72A4.2 4.2 0 0 0 15.82 4.1z"/></svg>`;
    } else {
        return `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg>`;
    }
}
"""
js = js + "\n" + icon_function
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("Re-added getAppIconMarkup")
