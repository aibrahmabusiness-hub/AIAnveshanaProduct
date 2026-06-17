import re
with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    js = f.read()

new_funcs = """function setupToolboxDragAndDrop() {
    const toolbox = document.getElementById('dynamic-toolbox');
    if (!toolbox) return;
    
    toolbox.addEventListener('dragstart', (e) => {
        const item = e.target.closest('.toolbox-item');
        if (item && item.dataset.node) {
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('text/plain', 'TOOLBOX:' + item.dataset.node);
        }
    });

    toolbox.addEventListener('click', (e) => {
        const item = e.target.closest('.toolbox-item');
        if (item && item.dataset.node) {
            addWorkflowStep(item.dataset.node);
        }
    });
}

function setupCanvasControls() {}
"""

js = re.sub(r'function initCustomCanvas\(\) \{', new_funcs + '\nfunction initCustomCanvas() {', js)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(js)
