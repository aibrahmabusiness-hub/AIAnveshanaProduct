import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add variable state
state_code = """
  const [variables, setVariables] = useState<{id: string; name: string; type: string; scope: string; value: string}[]>([]);
  const [newVar, setNewVar] = useState({name: '', type: 'String', scope: 'Input', value: ''});
"""
content = re.sub(r'(const \[isGmailExpanded.*?;\n)', r'\1' + state_code, content)

# 2. Add handleSaveWorkflow logic
# Note: we check if id is a number (V1 style) or string (V2 style).
save_code = """
  const handleSaveWorkflow = async () => {
    try {
      const payload = {
        agent_id: 1, // Default agent
        name: project?.name || 'Untitled Workflow',
        steps: { nodes, edges, variables },
        status: 'active'
      };
      
      let res;
      if (id === 'new_workflow' || isNaN(Number(id))) {
        res = await post('/api/workflows', payload);
        if (res.workflow_id) {
            window.history.replaceState({}, '', `/v2-canvas?id=${res.workflow_id}`);
        }
      } else {
        res = await put(`/api/workflows/${id}`, payload);
      }
      
      alert('Workflow saved successfully!');
    } catch (e: any) {
      alert('Error saving workflow: ' + e.message);
    }
  };
"""
# Replace existing handleSaveWorkflow if it exists, otherwise insert after handleExecuteWorkflow
if 'const handleSaveWorkflow' in content:
    content = re.sub(r'const handleSaveWorkflow = .*?};', save_code, content, flags=re.DOTALL)
else:
    content = re.sub(r'(const handleExecuteWorkflow = .*?};)', r'\1\n' + save_code, content, flags=re.DOTALL)

# 3. Update the button to use handleSaveWorkflow
content = content.replace(
    '''<button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50 rounded-md">
            <Save size={16} /> Save
          </button>''',
    '''<button onClick={handleSaveWorkflow} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50 rounded-md">
            <Save size={16} /> Save
          </button>'''
)

# 4. Implement Variables UI
variables_ui = """
            {activeLeftTab === 'variables' && (
              <div className="space-y-4">
                <div className="bg-white p-3 rounded-md border border-slate-200 shadow-sm">
                  <h3 className="text-xs font-bold text-slate-700 mb-2">Create Variable</h3>
                  <div className="space-y-2">
                    <input type="text" placeholder="Name" value={newVar.name} onChange={e => setNewVar({...newVar, name: e.target.value})} className="w-full text-xs p-1.5 border rounded" />
                    <div className="flex gap-2">
                      <select value={newVar.type} onChange={e => setNewVar({...newVar, type: e.target.value})} className="w-1/2 text-xs p-1.5 border rounded bg-white">
                        <option value="String">String</option>
                        <option value="Number">Number</option>
                        <option value="Boolean">Boolean</option>
                        <option value="Table">Table</option>
                        <option value="List">List</option>
                        <option value="Dictionary">Dictionary</option>
                      </select>
                      <select value={newVar.scope} onChange={e => setNewVar({...newVar, scope: e.target.value})} className="w-1/2 text-xs p-1.5 border rounded bg-white">
                        <option value="Input">Input</option>
                        <option value="Output">Output</option>
                      </select>
                    </div>
                    <button onClick={() => {
                      if (!newVar.name) return;
                      setVariables([...variables, { id: Math.random().toString(36).substr(2, 9), ...newVar }]);
                      setNewVar({name: '', type: 'String', scope: 'Input', value: ''});
                    }} className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs py-1.5 rounded font-medium">
                      Add Variable
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-slate-700">Existing Variables</h3>
                  {variables.length === 0 ? (
                    <div className="text-xs text-slate-500 italic text-center py-4">No variables created</div>
                  ) : (
                    variables.map(v => (
                      <div key={v.id} className="bg-white p-2 rounded-md border border-slate-200 flex flex-col gap-1 relative group">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-800">{v.name}</span>
                          <button onClick={() => setVariables(variables.filter(x => x.id !== v.id))} className="text-red-500 opacity-0 group-hover:opacity-100"><Trash2 size={12}/></button>
                        </div>
                        <div className="flex gap-2 text-[10px] text-slate-500">
                          <span className="bg-slate-100 px-1.5 py-0.5 rounded">{v.type}</span>
                          <span className="bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">{v.scope}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
"""

content = re.sub(
    r'\{activeLeftTab === \'variables\' && \(\s*<div className="text-sm text-slate-500 text-center py-8">\s*Variable management coming soon.\s*</div>\s*\)\}',
    variables_ui.replace('\\', '\\\\'),
    content
)

# Fix loading workflow state from backend if available
load_code = """
  // Load existing workflow
  useEffect(() => {
    if (id !== 'new_workflow' && id !== 'wf-live' && !isNaN(Number(id))) {
      get(`/api/workflows/${id}`).then((res) => {
        if (res.workflow) {
          setProject({ id: String(res.workflow.id), name: res.workflow.name, description: '' });
          if (res.workflow.steps) {
            setNodes(res.workflow.steps.nodes || []);
            setEdges(res.workflow.steps.edges || []);
            setVariables(res.workflow.steps.variables || []);
          }
        }
      }).catch(err => console.error("Error loading workflow", err));
    }
  }, [id, get, setNodes, setEdges, setVariables]);
"""
# insert before useEffect for WebSocket
if '// Initialize WebSocket connection' in content:
    content = content.replace('// Initialize WebSocket connection', load_code + '\n  // Initialize WebSocket connection')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
