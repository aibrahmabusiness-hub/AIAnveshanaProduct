import os

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

listeners = '''// Chat UI
const sendBtn = document.getElementById('sendBtn');
const promptInput = document.getElementById('promptInput');
const chatMessages = document.getElementById('chatMessages');

if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
if (promptInput) promptInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChatMessage(); });

// New Thread Button
document.getElementById('newThreadBtn').addEventListener('click', () => {
    activeThreadId = null;
    chatMessages.innerHTML = '';
    const greeting = document.getElementById('greetingText');
    if (greeting) greeting.style.display = 'block';
    
    document.querySelectorAll('.thread-item').forEach(el => el.classList.remove('active'));
    promptInput.focus();
});'''

# Notice document.getElementById('newThreadBtn') could throw TypeError if null
# Let's replace the whole block or comment it out
if "document.getElementById('newThreadBtn').addEventListener" in js:
    js = js.replace("document.getElementById('newThreadBtn').addEventListener", "if(document.getElementById('newThreadBtn')) document.getElementById('newThreadBtn').addEventListener")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Fixed newThreadBtn")
else:
    print("newThreadBtn listener not found")
