import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Delete everything from let availablePieces = []; onwards
match = re.search(r'let availablePieces = \[\];', content)
if match:
    content = content[:match.start()]

# Now append the fully correct code using python write_to_file
# wait, I will write the python script that appends the logic correctly!
with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
