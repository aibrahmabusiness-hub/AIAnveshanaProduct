import re

filepath = r"c:\Users\Admin\Documents\Agentic AI\v2\frontend\src\pages\Dashboard.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add `put` to `useApi`
content = content.replace(
    "const { get, post, del } = useApi();",
    "const { get, post, put, del } = useApi();"
)

# 2. Add `handleToggleStatus`
toggle_handler = """  const handleToggleStatus = async (workflow: Workflow) => {
    const newStatus = workflow.status === 'active' ? 'inactive' : 'active';
    // Optimistic UI update
    setWorkflows(workflows.map(w => w.id === workflow.id ? { ...w, status: newStatus } : w));
    try {
      await put(`/api/workflows/${workflow.id}/status`, { status: newStatus });
    } catch (err) {
      alert('Failed to update status');
      // Revert on failure
      setWorkflows(workflows.map(w => w.id === workflow.id ? { ...w, status: workflow.status } : w));
    }
  };

  const handleRunWorkflow"""

if "const handleToggleStatus" not in content:
    content = content.replace("  const handleRunWorkflow", toggle_handler)

# 3. Add onClick to the toggle div
old_toggle_div = """<div className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors 
${workflow.status === 'active' ? 'bg-[#22c55e]' : 'bg-slate-200'}`}>"""

new_toggle_div = """<div 
                          onClick={() => handleToggleStatus(workflow)}
                          className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${workflow.status === 'active' ? 'bg-[#22c55e]' : 'bg-slate-200'}`}>"""

# Note: In the source code, there is a newline in the template string `\n${workflow.status...`
# Let's use regex to find the div
pattern = re.compile(r'<div className=\{`w-10 h-5 rounded-full relative cursor-pointer transition-colors \s*\$\{workflow\.status === \'active\' \? \'bg-\[\#22c55e\]\' : \'bg-slate-200\'\}`\}>')
content = re.sub(pattern, new_toggle_div, content)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Dashboard.tsx patched successfully.")
