import re

with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.html", "r", encoding="utf-8") as f:
    html = f.read()

start_marker = "<!-- Left Toolbox -->"
end_marker = "<!-- Center List Container -->"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_toolbox = """<!-- Left Toolbox -->
                <div style="width:280px; background:#fff; border-right:1px solid #e2e8f0; display:flex; flex-direction:column; overflow-y:auto;">
                    <div style="padding:16px; border-bottom:1px solid #f1f5f9;">
                        <h3 style="margin:0; font-size:1rem; font-weight:700; color:#0f172a;">Pieces & Apps</h3>
                        <p style="margin:4px 0 0 0; font-size:0.75rem; color:#64748b;">Drag nodes into the flow</p>
                    </div>
                    <div id="dynamic-toolbox" style="padding:16px; display:flex; flex-direction:column; gap:12px;">
                        <div style="text-align:center; color:#94a3b8; font-size:0.85rem; padding:20px;">Loading apps...</div>
                    </div>
                </div>
                """
    
    new_html = html[:start_idx] + new_toolbox + html[end_idx:]
    with open(r"C:\Users\Admin\Documents\Agentic AI\frontend\project.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Successfully replaced toolbox")
else:
    print("Could not find markers")
