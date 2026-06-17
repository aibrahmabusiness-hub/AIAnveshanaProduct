import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Eradicate the style block inside createNode
content = re.sub(
    r'position,\s*style:\s*\{[^}]+\},\s*\};',
    r'position,\n      };',
    content,
    flags=re.MULTILINE
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
