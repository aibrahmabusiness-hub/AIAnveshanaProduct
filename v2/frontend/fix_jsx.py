import re
with open(r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace from the end of the tabs up to fitView
pattern = r'(Triggers\s*</button>\s*</div>)[\s\S]*?(fitView)'

replacement = r'''\1
          
          <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
            {activeLeftTab === 'activities' && (
              <div className="space-y-2">
                <div className="mb-4">
                  <input
                    type="text"
                    placeholder="Search elements"
                    className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>
                
                <div>
                  <button
                    onClick={() => setIsGmailExpanded(!isGmailExpanded)}
                    className="flex items-center gap-2 w-full text-left py-1 text-sm font-semibold text-slate-700 hover:text-blue-600"
                  >
                    {isGmailExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    Gmail
                  </button>
                  
                  {isGmailExpanded && (
                    <div className="ml-5 mt-1 space-y-1">
                      {WORKFLOW_PIECES.filter(p => p.name === 'gmail').map((piece) => (
                        <div key={piece.name} className="flex flex-col gap-1">
                          {['Send Email', 'Read Email', 'Search Email'].map(actionName => (
                            <button
                              key={actionName}
                              draggable
                              onDragStart={(e) => {
                                e.dataTransfer.setData('application/reactflow', JSON.stringify({
                                  name: piece.name,
                                  displayName: `Gmail: ${actionName}`,
                                  category: piece.category,
                                  description: piece.description,
                                }));
                                e.dataTransfer.effectAllowed = 'move';
                              }}
                              className="flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-blue-50 rounded cursor-grab active:cursor-grabbing w-full text-left"
                            >
                              <div className="w-4 h-4 bg-blue-100 rounded text-blue-600 flex items-center justify-center shrink-0">G</div>
                              <span className="truncate">{actionName}</span>
                            </button>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {activeLeftTab === 'variables' && (
              <div className="text-sm text-slate-500 text-center py-8">
                Variable management coming soon.
              </div>
            )}
            
            {activeLeftTab === 'triggers' && (
              <div className="space-y-2">
                {WORKFLOW_PIECES.filter(p => p.category === 'Triggers').map((piece) => (
                  <button
                    key={piece.name}
                    draggable
                    onDragStart={(e) => onDragStart(e, piece)}
                    className="flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-emerald-50 rounded cursor-grab active:cursor-grabbing w-full text-left"
                  >
                    <div className="w-4 h-4 bg-emerald-100 rounded text-emerald-600 flex items-center justify-center shrink-0">T</div>
                    <span className="truncate">{piece.displayName}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* Canvas Area */}
        <div ref={wrapperRef} className="flex-1 bg-slate-50 relative" onDrop={onDrop} onDragOver={onDragOver}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={(instance) => setReactFlowInstance(instance)}
            onNodeClick={(_, node) => setSelectedNode(node.id)}
            \2'''

# Fix the JSX
content = re.sub(pattern, replacement, content)

with open(r'c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
