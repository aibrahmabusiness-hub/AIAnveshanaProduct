import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# apFetch ends at:
#         throw error;
#     }
# }

# We want to find:
pattern = r'(async function apFetch.*?^\}\n).*?(async function loadWorkflowsView.*?\{)'
match = re.search(pattern, content, flags=re.DOTALL | re.MULTILINE)
if match:
    print("Found the orphaned block. Replacing...")
    new_content = content[:match.start(0)] + match.group(1) + "\n\n" + match.group(2) + content[match.end(0):]
    with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Could not find pattern")

