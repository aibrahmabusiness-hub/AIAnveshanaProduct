import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\frontend\project.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("frame.src = `/v2-canvas?id=new_workflow&agent_id=${agentId}`;", "frame.src = `/v2-canvas?id=new_workflow&agent_id=${agentId}&t=${Date.now()}`;")
content = content.replace("frame.src = `/v2-canvas?id=${currentFlowId}&agent_id=${agentId}`;", "frame.src = `/v2-canvas?id=${currentFlowId}&agent_id=${agentId}&t=${Date.now()}`;")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
