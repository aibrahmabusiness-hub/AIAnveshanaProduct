import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

history_logic = '''        // Show/hide history panel based on view
        const historyPanel = document.getElementById('historyPanel');
        historyPanel.style.display = viewId === 'chat' ? '' : 'none';'''
        
if history_logic in js:
    js = js.replace(history_logic, "")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Removed history logic")
else:
    print("History logic not found. Trying regex.")
    js = re.sub(r"// Show/hide history panel based on view\s+const historyPanel = document\.getElementById\('historyPanel'\);\s+historyPanel\.style\.display = [^;]+;", "", js)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Removed via regex")
