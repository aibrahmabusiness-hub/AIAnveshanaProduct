import re

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'r', encoding='utf-8') as f:
    content = f.read()

correct_loadPieces = '''async function loadPieces() {
    try {
        const res = await authFetch('/api/pieces');
        if (res.ok) {
            const data = await res.json();
            availablePieces = data.pieces || [];
        } else {
            console.warn('Backend returned error for pieces', res.status);
            availablePieces = [];
        }
        populateToolbox();
    } catch (err) {
        console.error('Failed to load pieces', err);
        const toolbox = document.getElementById('dynamic-toolbox');
        if (toolbox) {
            toolbox.innerHTML = '<div style="color:red; padding:10px;">Failed to load apps</div>';
        }
    }
}'''

content = re.sub(r'async function loadPieces\(\) \{.*?\}\s*\}', correct_loadPieces, content, flags=re.DOTALL)

with open('C:/Users/Admin/Documents/Agentic AI/frontend/project.js', 'w', encoding='utf-8') as f:
    f.write(content)
