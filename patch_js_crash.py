import re

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Replace assignments
js = re.sub(r"const promptInput = document\.getElementById\('promptInput'\);\n?", "", js)
js = re.sub(r"const sendBtn = document\.getElementById\('sendBtn'\);\n?", "", js)
js = re.sub(r"const chatMessages = document\.getElementById\('chatMessages'\);\n?", "", js)
js = re.sub(r"const newThreadBtn = document\.getElementById\('newThreadBtn'\);\n?", "", js)

# Replace listeners (using if checks or just removing them)
# sendBtn.addEventListener('click', sendMessage);
js = re.sub(r"sendBtn\.addEventListener\('click',\s*sendMessage\);\n?", "", js)
# promptInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
js = re.sub(r"promptInput\.addEventListener\('keypress',.*?\);\n?", "", js)
# newThreadBtn.addEventListener('click', async () => { ... });
js = re.sub(r"newThreadBtn\.addEventListener\('click',\s*async\s*\(\)\s*=>\s*\{.*?\}\);\n?", "", js, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("Removed top-level chat variables and listeners")
