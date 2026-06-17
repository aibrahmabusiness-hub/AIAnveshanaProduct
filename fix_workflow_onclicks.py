import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("openWorkflowEditor()", "openWorkflowEditor('')")
content = content.replace("deleteWorkflow()", "deleteWorkflow('')")

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
