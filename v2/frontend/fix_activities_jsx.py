import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace the `activeLeftTab === 'activities'` block.
# We will use regex to find it and replace it.

pattern = re.compile(r"(\{activeLeftTab === 'activities' && \(\s*<div className=\"space-y-2\">\s*<div className=\"mb-4\">.*?</div>\s*\)\}\s*</div>\s*\)\})", re.DOTALL)

# Let's see if we can find the start of `activeLeftTab === 'activities'`
start_idx = content.find("{activeLeftTab === 'activities' && (")
if start_idx != -1:
    # Find the end of this block by counting braces
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx != -1:
        # We found the block
        # Now we replace it with dynamic categories
        dynamic_block = """{activeLeftTab === 'activities' && (
              <div className="space-y-2">
                <div className="mb-4">
                  <input
                    type="text"
                    placeholder="Search elements"
                    value={searchPiece}
                    onChange={(e) => setSearchPiece(e.target.value)}
                    className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>
                
                {Object.entries(groupedPieces)
                  .filter(([category]) => category !== 'Triggers')
                  .map(([category, pieces]) => (
                  <div key={category} className="mb-2">
                    <div className="flex items-center gap-2 w-full text-left py-1 text-sm font-semibold text-slate-700">
                      <ChevronDown size={14} />
                      {category}
                    </div>
                    
                    <div className="ml-5 mt-1 space-y-1">
                      {pieces.map((piece) => (
                        <div key={piece.name} className="flex flex-col gap-1">
                          <button
                            draggable
                            onDragStart={(e) => {
                              e.dataTransfer.setData('application/reactflow', JSON.stringify({
                                name: piece.name,
                                displayName: piece.displayName,
                                category: piece.category,
                                description: piece.description,
                              }));
                              e.dataTransfer.effectAllowed = 'move';
                            }}
                            className="flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded cursor-grab active:cursor-grabbing w-full text-left"
                          >
                            <div className="w-4 h-4 bg-slate-200 rounded text-slate-600 flex items-center justify-center shrink-0">
                              {piece.displayName.charAt(0)}
                            </div>
                            <span className="truncate">{piece.displayName}</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}"""
        
        new_content = content[:start_idx] + dynamic_block + content[end_idx:]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated Project.tsx!")
    else:
        print("Could not find end of block.")
else:
    print("Could not find start of block.")
