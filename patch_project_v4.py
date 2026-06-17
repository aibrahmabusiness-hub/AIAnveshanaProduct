import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "r", encoding="utf-8") as f:
    content = f.read()

# Replace all remaining instances of agentData with activeAgentData
content = re.sub(r'\bagentData\b', 'activeAgentData', content)

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced all agentData with activeAgentData successfully.")
