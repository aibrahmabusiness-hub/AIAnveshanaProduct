import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any occurrence of list.innerHTML = <div... with list.innerHTML = <div...
content = re.sub(r'(list\.innerHTML\s*=\s*)(<div)', r'\1\2', content)

# Replace any occurrence of </div>; with </div>;
content = re.sub(r'(</div>)(\s*;)', r'\1\2', content)

# Replace wf => <div with wf => <div
content = re.sub(r'(wf\s*=>\s*)(<div)', r'\1\2', content)

# Replace conn => <div with conn => <div
content = re.sub(r'(conn\s*=>\s*)(<div)', r'\1\2', content)

# Replace </div> ).join(''); with </div> ).join('');
content = re.sub(r'(</div>)(\s*\)\.join)', r'\1\2', content)

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
