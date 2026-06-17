import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update loadConnectedAppsWidget to use getAppIconMarkup
old_apps_widget = """const apps = [
        { key: 'gmail', name: 'Gmail', icon: '✉️', color: 'linear-gradient(135deg, #f87171, #ef4444)' },
        { key: 'jira', name: 'Jira', icon: '💎', color: 'linear-gradient(135deg, #60a5fa, #3b82f6)' },
        { key: 'servicenow', name: 'ServiceNow', icon: '⚡', color: 'linear-gradient(135deg, #34d399, #059669)' },
        { key: 'salesforce', name: 'Salesforce', icon: '☁️', color: 'linear-gradient(135deg, #38bdf8, #0ea5e9)' }
    ];"""

new_apps_widget = """const apps = [
        { key: 'gmail', name: 'Gmail', icon: getAppIconMarkup('gmail'), isSvg: true },
        { key: 'jira', name: 'Jira', icon: getAppIconMarkup('jira'), isSvg: true },
        { key: 'servicenow', name: 'ServiceNow', icon: getAppIconMarkup('servicenow'), isSvg: true },
        { key: 'salesforce', name: 'Salesforce', icon: getAppIconMarkup('salesforce'), isSvg: true }
    ];"""

if old_apps_widget in content:
    content = content.replace(old_apps_widget, new_apps_widget)

old_app_card = """<div style="width:40px; height:40px; background:${app.color}; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.4rem; box-shadow:0 4px 6px rgba(0,0,0,0.05);">${app.icon}</div>"""

new_app_card = """<div style="width:40px; height:40px; ${app.isSvg ? '' : 'background:' + app.color + ';'} color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.4rem; box-shadow:0 4px 6px rgba(0,0,0,0.05);">${app.icon}</div>"""

if old_app_card in content:
    content = content.replace(old_app_card, new_app_card)

# 2. Update loadToolsView to use getAppIconMarkup
old_tools_title = """<div class="tools-group-title">
                        <strong>${group.name}</strong>
                    </div>"""

new_tools_title = """<div class="tools-group-title" style="display: flex; align-items: center; gap: 12px;">
                        ${getAppIconMarkup(group.id)}
                        <strong style="font-size:1.1rem; color:#0f172a;">${group.name}</strong>
                    </div>"""

if old_tools_title in content:
    content = content.replace(old_tools_title, new_tools_title)

# Ensure getAppIconMarkup supports 'gmail' without activepieces prefix
old_get_icon = "const type = nodeType.replace('@activepieces/piece-', '').toLowerCase();"
new_get_icon = "const type = nodeType.replace('@activepieces/piece-', '').toLowerCase();"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched project.js successfully")
