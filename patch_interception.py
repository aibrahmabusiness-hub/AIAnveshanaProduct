import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\workflows.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_interception = """        elif "::" in node_type:
            # Activepieces piece execution
            import requests
            try:
                piece_name, action_name = node_type.split("::", 1)"""

new_interception = """        elif "::" in node_type:
            # Activepieces piece execution
            import requests
            try:
                piece_name, action_name = node_type.split("::", 1)
                
                # --- UNIFIED ARCHITECTURE INTERCEPTION ---
                # Route specific pieces directly to the Python TOOL_REGISTRY instead of Node.js
                unified_mapping = {
                    "@activepieces/piece-servicenow": {
                        "servicenow_incidents::create_incident": "servicenow_incidents",
                        "servicenow_incidents::get_incidents": "servicenow_incidents",
                        "servicenow_incidents::update_incident": "servicenow_incidents",
                        "servicenow_tables::query_table": "servicenow_tables"
                    },
                    "@activepieces/piece-salesforce": {
                        "salesforce_query::query_salesforce": "salesforce_query",
                        "salesforce_create::create_salesforce_record": "salesforce_create"
                    }
                }
                
                if piece_name in unified_mapping and action_name in unified_mapping[piece_name]:
                    tool_key = unified_mapping[piece_name][action_name]
                    
                    # Determine which specific function index to call based on action
                    funcs = TOOL_REGISTRY[tool_key]["functions"]
                    if not funcs:
                        raise Exception(f"Tool {tool_key} has no functions registered")
                        
                    func_index = 0
                    if action_name == "servicenow_incidents::get_incidents": func_index = 1
                    elif action_name == "servicenow_incidents::update_incident": func_index = 2
                    
                    # Execute purely in Python
                    output_data = funcs[func_index](**resolved)
                    results.append({"tool": node_type, "status": "success", "output": str(output_data)})
                    global_context[f"{nid}_output"] = output_data
                    for next_id in adj.get(nid, []):
                        visit(next_id)
                    return
                # --- END INTERCEPTION ---"""

if old_interception in content:
    content = content.replace(old_interception, new_interception)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched workflows.py successfully.")
else:
    print("Could not find interception block.")
