import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Strip styles from loaded nodes
old_set_nodes = """          if (canvasData && canvasData.nodes) {
            setNodes(canvasData.nodes);
            setEdges(canvasData.edges || []);"""

new_set_nodes = """          if (canvasData && canvasData.nodes) {
            // Strip any legacy style props to prevent giant background blobs
            setNodes(canvasData.nodes.map((n: any) => { const { style, ...rest } = n; return rest; }));
            setEdges(canvasData.edges || []);"""
content = content.replace(old_set_nodes, new_set_nodes)

# 2. Update background to explicit dots
old_background = """<Background gap={20} size={1} color="#e2e8f0" />"""
new_background = """<Background variant="dots" gap={16} size={1} color="#cbd5e1" />"""
content = content.replace(old_background, new_background)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
