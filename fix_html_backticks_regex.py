import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <div... with <div...
content = re.sub(r'(list\.innerHTML\s*=\s*)(<div)', r'\1\2', content)
# Replace </div>; with </div>;
content = re.sub(r'(</div>)(\s*;)', r'\1\2', content)

# For workflows.map(wf => <div...</div> ).join('');
content = re.sub(r'(\=\s*workflows\.map\(wf\s*=>\s*)(<div)', r'\1\2', content)
content = re.sub(r'(</div>)(\s*\)\.join)', r'\1\2', content)

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
