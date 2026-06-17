import re
with open(r"C:\Users\Admin\Documents\Agentic AI\backend\workflows.py", "r", encoding="utf-8") as f:
    code = f.read()

new_logic = """
        elif "::" in node_type:
            # Activepieces piece execution
            import requests
            try:
                piece_name, action_name = node_type.split("::", 1)
                payload = {
                    "pieceName": piece_name,
                    "actionName": action_name,
                    "input": resolved
                }
                res = requests.post("http://localhost:3001/execute", json=payload, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("success"):
                        output_data = data.get("result")
                        results.append({"tool": node_type, "status": "success", "output": output_data})
                    else:
                        output_data = f"Piece Error: {data.get('error')}"
                        results.append({"tool": node_type, "status": "failed", "output": output_data})
                else:
                    output_data = f"HTTP {res.status_code}: {res.text}"
                    results.append({"tool": node_type, "status": "failed", "output": output_data})
            except Exception as e:
                output_data = f"Engine Error: {str(e)}"
                results.append({"tool": node_type, "status": "failed", "output": output_data})
"""

# We need to insert this right after `elif node_type == "data_table": ...` inside `visit` function and inside `execute_workflow` loop.

import re

# For execute_workflow_from_canvas
code = re.sub(
    r'(elif node_type == "data_table":\s*output_data = "Data manipulation completed"\s*results\.append\({"tool": node_type, "status": "success", "output": output_data}\))',
    r'\1' + new_logic,
    code
)

# For execute_workflow (linear steps list)
new_logic_linear = """
                    elif "::" in tool_id:
                        import requests
                        try:
                            piece_name, action_name = tool_id.split("::", 1)
                            payload = {
                                "pieceName": piece_name,
                                "actionName": action_name,
                                "input": resolved
                            }
                            res = requests.post("http://localhost:3001/execute", json=payload, timeout=30)
                            if res.status_code == 200:
                                data = res.json()
                                if data.get("success"):
                                    output_data = data.get("result")
                                    results.append({"tool": tool_id, "status": "success", "output": output_data})
                                else:
                                    output_data = f"Piece Error: {data.get('error')}"
                                    results.append({"tool": tool_id, "status": "failed", "output": output_data})
                            else:
                                output_data = f"HTTP {res.status_code}: {res.text}"
                                results.append({"tool": tool_id, "status": "failed", "output": output_data})
                        except Exception as e:
                            output_data = f"Engine Error: {str(e)}"
                            results.append({"tool": tool_id, "status": "failed", "output": output_data})
"""

code = re.sub(
    r'(elif tool_id\.startswith\("trigger_"\):\s*output_data = "Triggered"\s*results\.append\({"tool": tool_id, "status": "success", "output": output_data}\))',
    r'\1' + new_logic_linear,
    code
)

with open(r"C:\Users\Admin\Documents\Agentic AI\backend\workflows.py", "w", encoding="utf-8") as f:
    f.write(code)
