import os

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

js = js.replace("loadChatThreads();", "")
js = js.replace("await loadChatThreads();", "")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("Removed remaining calls")
