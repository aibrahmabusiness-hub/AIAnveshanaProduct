import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the missing backticks in loadWorkflowsView
content = content.replace("list.innerHTML = <div", "list.innerHTML = <div")
content = content.replace("</div>;", "</div>;")
content = content.replace("list.innerHTML = workflows.map(wf => \n            <div", "list.innerHTML = workflows.map(wf => \n            <div")
content = content.replace("</div>\n        ).join('');", "</div>\n        ).join('');")

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)

