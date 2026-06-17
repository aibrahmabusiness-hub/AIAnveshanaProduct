import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the /api/pieces route
match = re.search(r'@app\.get\("/api/pieces"\).*?(?=\Z|# Serve static files)', content, re.DOTALL)
if match:
    pieces_route = match.group(0)
    # Remove it from its current position
    content = content[:match.start()] + content[match.end():]
    
    # Insert it before app.mount("/", ...)
    mount_match = re.search(r'# Serve static files and index', content)
    if mount_match:
        content = content[:mount_match.start()] + pieces_route + '\n\n' + content[mount_match.start():]
        
        with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
            f.write(content)
