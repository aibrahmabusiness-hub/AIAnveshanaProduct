import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Replace any occurrence of chat UI code with empty string.
# Rather than trying to match large blocks of functions exactly, I can use regex to remove loadChatThreads, loadThreadHistory, sendChatMessage, etc.
patterns = [
    r"async function loadChatThreads\(\) \{.*?\n\}\n",
    r"async function loadThreadHistory\(.*?\) \{.*?\n\}\n",
    r"async function deleteThread\(.*?\) \{.*?\n\}\n",
    r"async function sendChatMessage\(\) \{.*?\n\}\n",
    r"function appendMessage\(.*?\) \{.*?\n\}\n"
]

for p in patterns:
    js = re.sub(p, "", js, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("Removed chat functions")
