with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''        // Lazy-load workflows view when tab is clicked
        if (viewId === 'workflows') {
            loadWorkflowsView();
        }
        if (viewId === 'connections') {
            loadConnectionsView();
        }'''

if "viewId === 'connections'" not in content:
    content = content.replace('''        // Lazy-load workflows view when tab is clicked
        if (viewId === 'workflows') {
            loadWorkflowsView();
        }''', new_code)

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
