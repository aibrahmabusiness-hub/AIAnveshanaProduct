import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Project.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
if "Clock" not in content:
    content = content.replace("ChevronRight, X } from 'lucide-react';", "ChevronRight, X, Clock, Repeat, GitBranch, Timer, Webhook, Bot } from 'lucide-react';")

# 2. Add renderIcon function
render_icon_func = """
  const renderIcon = (p: string) => {
    if (p === 'manual') return <Play className="w-5 h-5 text-emerald-600" />;
    if (p === 'schedule') return <Clock className="w-5 h-5 text-emerald-600" />;
    if (p === 'logic_loop' || p === 'loop') return <Repeat className="w-5 h-5 text-blue-600" />;
    if (p === 'condition') return <GitBranch className="w-5 h-5 text-blue-600" />;
    if (p === 'delay') return <Timer className="w-5 h-5 text-blue-600" />;
    if (p === 'webhook') return <Webhook className="w-5 h-5 text-slate-600" />;
    if (p === 'ai_agent') return <Bot className="w-5 h-5 text-purple-600" />;
    
    // Custom simpleicons URL for others
    const cdnName = p.split('_')[0]; // Extract the base app name (e.g. gmail_read_email -> gmail)
    return <img src={`https://cdn.simpleicons.org/${cdnName}`} alt={p} className="w-5 h-5 object-contain" onError={(e) => {
      (e.target as HTMLImageElement).src = 'https://cdn.simpleicons.org/appwrite'; // generic fallback
    }} />;
  };
"""

if "const renderIcon =" not in content:
    # Insert it right before the return statement of Project
    content = content.replace("return (", render_icon_func + "\n  return (", 1)

# 3. Replace the placeholder div with renderIcon in triggers and activities
# We have a block:
# <div className="w-4 h-4 bg-slate-200 rounded text-slate-600 flex items-center justify-center shrink-0">
#   {piece.displayName.charAt(0)}
# </div>

placeholder_pattern = re.compile(r'<div className="w-4 h-4 bg-[^>]+>\s*\{piece\.displayName\.charAt\(0\)\}\s*</div>', re.DOTALL)
new_icon_block = """<div className="w-6 h-6 flex items-center justify-center shrink-0">
                              {renderIcon(piece.name)}
                            </div>"""

content = placeholder_pattern.sub(new_icon_block, content)

# 4. We also have a hardcoded Trigger tab block
placeholder_pattern_triggers = re.compile(r'<div className="w-4 h-4 bg-[^>]+>\s*T\s*</div>', re.DOTALL)
content = placeholder_pattern_triggers.sub(new_icon_block, content)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Project.tsx logos patched.")
