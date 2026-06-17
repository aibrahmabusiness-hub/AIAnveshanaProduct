import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update nodeTypes mapping
old_node_types = """const nodeTypes: NodeTypes = {
  default: BaseNode,
};"""
new_node_types = """const nodeTypes: NodeTypes = {
  customNode: BaseNode,
  default: BaseNode, // Fallback for legacy
};"""
content = content.replace(old_node_types, new_node_types)

# 2. Update createNode function
old_create_node = """      const newNode: Node = {
        id: newNodeId,
        type: 'default',
        data: { label: piece.displayName, piece: piece.name, config: {} },
        position,
        };"""
new_create_node = """      const newNode: Node = {
        id: newNodeId,
        type: 'customNode',
        data: { label: piece.displayName, piece: piece.name, config: {} },
        position,
        };"""
content = content.replace(old_create_node, new_create_node)

# 3. Update loading logic for existing nodes
old_set_nodes = """          if (canvasData && canvasData.nodes) {
            // Strip any legacy style props to prevent giant background blobs
            setNodes(canvasData.nodes.map((n: any) => { const { style, ...rest } = n; return rest; }));
            setEdges(canvasData.edges || []);"""
new_set_nodes = """          if (canvasData && canvasData.nodes) {
            // Strip any legacy style props to prevent giant background blobs and upgrade type
            setNodes(canvasData.nodes.map((n: any) => { 
              const { style, ...rest } = n; 
              return { ...rest, type: 'customNode' }; 
            }));
            setEdges(canvasData.edges || []);"""
content = content.replace(old_set_nodes, new_set_nodes)

# 4. Update the fallback startNode
old_start_node = """        const startNode: Node = {
          id: 'manual-1',
          type: 'default',
          position: { x: 250, y: 150 },
          data: { label: 'Start Event', piece: 'manual', config: {} },
        };"""
new_start_node = """        const startNode: Node = {
          id: 'manual-1',
          type: 'customNode',
          position: { x: 250, y: 150 },
          data: { label: 'Start Event', piece: 'manual', config: {} },
        };"""
content = content.replace(old_start_node, new_start_node)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
