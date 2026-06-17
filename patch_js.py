import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

def replace_if_found(target, replacement, js_code):
    if target in js_code:
        return js_code.replace(target, replacement)
    return js_code

# Remove chat resizer logic
resizer = '''// Chat Resizer
let isResizing = false;
const resizeHandle = document.getElementById('resizeHandle');
const historyPanel = document.getElementById('historyPanel');

if (resizeHandle) {
    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.style.cursor = 'ew-resize';
    });

    window.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const newWidth = e.clientX;
        if (newWidth > 200 && newWidth < 500) {
            historyPanel.style.width = newWidth + 'px';
        }
    });

    window.addEventListener('mouseup', () => {
        isResizing = false;
        document.body.style.cursor = 'default';
    });
}'''
js = replace_if_found(resizer, "", js)

# Remove all chat-related logic from JS using regex or string replacement
# We'll just replace the specific listeners

chat_listeners = '''// Chat UI
const sendBtn = document.getElementById('sendBtn');
const promptInput = document.getElementById('promptInput');
const chatMessages = document.getElementById('chatMessages');

if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
if (promptInput) promptInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChatMessage(); });'''
js = replace_if_found(chat_listeners, "", js)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("Updated JS")
