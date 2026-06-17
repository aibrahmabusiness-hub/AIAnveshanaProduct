import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("node.style.transform = 'translate(-50%, -50%)';", "node.style.transform = 'translate(-50%, -50%)';\n        node.style.position = 'absolute';")

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
