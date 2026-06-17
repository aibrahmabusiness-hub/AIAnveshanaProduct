import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Enhance executionLogs type
old_log_state = "const [executionLogs, setExecutionLogs] = useState<{message: string; timestamp: string; type: 'info' | 'success' | 'error'}[]>([]);"
new_log_state = """const [executionLogs, setExecutionLogs] = useState<{
    message: string;
    timestamp: string;
    type: 'info' | 'success' | 'error';
    nodeId?: string;
    inputs?: any;
    result?: any;
    duration?: number;
  }[]>([]);
  const [showDebugPanel, setShowDebugPanel] = useState(false);"""
content = content.replace(old_log_state, new_log_state)

# 2. Add showDebugPanel = true on execution
old_execute = """const data = await post(`/api/workflows/${id}/execute`, { nodes, edges, variables });"""
new_execute = """setShowDebugPanel(true);
        const data = await post(`/api/workflows/${id}/execute`, { nodes, edges, variables });"""
content = content.replace(old_execute, new_execute)

# 3. Update the node_success and node_error events to capture the new payload data
old_node_success = """        case 'node_success':
          setNodeStatus(prev => ({
            ...prev,
            [eventData.node_id]: {
              status: 'success',
              message: `Completed: ${JSON.stringify(eventData.result?.message || eventData.result)}`,
            }
          }));
          setExecutionLogs(prev => [...prev, {
            message: `Success: ${eventData.node_id}`,
            timestamp: new Date().toISOString(),
            type: 'success'
          }]);
          break;"""
new_node_success = """        case 'node_success':
          setNodeStatus(prev => ({
            ...prev,
            [eventData.node_id]: {
              status: 'success',
              message: `Completed`,
            }
          }));
          setExecutionLogs(prev => [...prev, {
            message: `Success: ${eventData.node_id}`,
            timestamp: new Date().toISOString(),
            type: 'success',
            nodeId: eventData.node_id,
            result: eventData.result,
            inputs: eventData.inputs,
            duration: eventData.duration
          }]);
          break;"""
content = content.replace(old_node_success, new_node_success)

old_node_error = """        case 'node_error':
          setNodeStatus(prev => ({
            ...prev,
            [eventData.node_id]: {
              status: 'error',
              error: eventData.error,
            }
          }));
          setExecutionLogs(prev => [...prev, {
            message: `Error: ${eventData.error}`,
            timestamp: new Date().toISOString(),
            type: 'error'
          }]);
          break;"""
new_node_error = """        case 'node_error':
          setNodeStatus(prev => ({
            ...prev,
            [eventData.node_id]: {
              status: 'error',
              error: eventData.error,
            }
          }));
          setExecutionLogs(prev => [...prev, {
            message: `Error: ${eventData.error}`,
            timestamp: new Date().toISOString(),
            type: 'error',
            nodeId: eventData.node_id,
            result: eventData.error,
            inputs: eventData.inputs,
            duration: eventData.duration
          }]);
          break;"""
content = content.replace(old_node_error, new_node_error)

# 4. Render the bottom panel
old_main_area = """        {/* Center Canvas */}
        <div className="flex-1 relative bg-slate-50 flex flex-col">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedNode(node.id)}
            onPaneClick={() => setSelectedNode(null)}
            fitView
            className="flex-1"
          >
            <Background color="#cbd5e1" gap={16} />
            <Controls />
          </ReactFlow>
        </div>"""

new_main_area = """        {/* Center Canvas */}
        <div className="flex-1 relative bg-slate-50 flex flex-col">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedNode(node.id)}
            onPaneClick={() => setSelectedNode(null)}
            fitView
            className="flex-1"
          >
            <Background color="#cbd5e1" gap={16} />
            <Controls />
          </ReactFlow>
          
          {/* Bottom Debug Panel */}
          {showDebugPanel && (
            <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-white border-t border-slate-200 shadow-lg flex flex-col z-50">
              <div className="flex items-center justify-between px-4 py-2 bg-slate-100 border-b border-slate-200">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                  <Play size={14} /> Execution Debug Panel
                </div>
                <button onClick={() => setShowDebugPanel(false)} className="text-slate-400 hover:text-slate-600">
                  <X size={16} />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 font-mono text-xs">
                {executionLogs.length === 0 && (
                  <div className="text-slate-400 italic">Waiting for execution to start...</div>
                )}
                {executionLogs.map((log, i) => (
                  <div key={i} className={`p-3 rounded border ${
                    log.type === 'error' ? 'bg-red-50 border-red-100' :
                    log.type === 'success' ? 'bg-green-50 border-green-100' :
                    'bg-slate-50 border-slate-100'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`font-semibold ${
                        log.type === 'error' ? 'text-red-700' :
                        log.type === 'success' ? 'text-green-700' :
                        'text-blue-700'
                      }`}>
                        [{log.timestamp.split('T')[1].split('.')[0]}] {log.message}
                      </span>
                      {log.duration !== undefined && (
                        <span className="text-slate-500">{log.duration}ms</span>
                      )}
                    </div>
                    {log.inputs && Object.keys(log.inputs).length > 0 && (
                      <div className="mt-2">
                        <span className="text-slate-500 font-semibold text-[10px] uppercase">Inputs</span>
                        <pre className="mt-1 bg-white p-2 rounded border border-slate-200 overflow-x-auto text-slate-700">
                          {JSON.stringify(log.inputs, null, 2)}
                        </pre>
                      </div>
                    )}
                    {log.result && (
                      <div className="mt-2">
                        <span className="text-slate-500 font-semibold text-[10px] uppercase">Output</span>
                        <pre className="mt-1 bg-white p-2 rounded border border-slate-200 overflow-x-auto text-slate-700">
                          {typeof log.result === 'object' ? JSON.stringify(log.result, null, 2) : log.result}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>"""
content = content.replace(old_main_area, new_main_area)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# 5. Fix X icon import
old_lucide = "from 'lucide-react';"
new_lucide = "X, from 'lucide-react';"
content = content.replace(old_lucide, new_lucide)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

