import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('http://localhost:3000/api/v1/pieces', 'http://127.0.0.1:3000/api/v1/pieces')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
