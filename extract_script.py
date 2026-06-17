import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract from 'class WorkflowCreateRequest' down to '# --- Health ---'
match = re.search(r'(class WorkflowCreateRequest.*?)(?=# --- Health ---)', content, re.DOTALL)
if match:
    with open('C:/Users/Admin/Documents/Agentic AI/extracted_endpoints.py', 'w', encoding='utf-8') as out:
        out.write(match.group(1))
