import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\frontend\project.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("switchWorkflowVersion('v1')", "switchWorkflowVersion('v2')")
content = content.replace("window.preferredWorkflowVersion = 'v1'", "window.preferredWorkflowVersion = 'v2'")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
