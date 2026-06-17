import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

bad_str1 = "if (!confirm(Are you sure you want to remove the connection for ?)) return;"
good_str1 = "if (!confirm(Are you sure you want to remove the connection for ?)) return;"

bad_str2 = "const res = await authFetch(/api/credentials/, { method: 'DELETE' });"
good_str2 = "const res = await authFetch(/api/credentials/, { method: 'DELETE' });"

content = content.replace(bad_str1, good_str1)
content = content.replace(bad_str2, good_str2)

# Also check for init() at the bottom!
if "init();" not in content[-500:]:
    content += "\n// Initialize the page\ninit();\n"

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
