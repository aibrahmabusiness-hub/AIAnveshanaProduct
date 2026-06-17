import json
import contextvars
from database import get_workflow, current_user_id
from tools.tool_registry import TOOL_REGISTRY

def resolve_params(params: dict, input_data: dict) -> dict:
    """Resolve {{placeholder}} values in params dict using input_data."""
    resolved = {}
    for k, v in params.items():
        if isinstance(v, str):
            val = v
            for key, input_val in input_data.items():
                val = val.replace(f"{{{{{key}}}}}", str(input_val))
            resolved[k] = val
        elif isinstance(v, dict):
            resolved[k] = resolve_params(v, input_data)
        elif isinstance(v, list):
            resolved_list = []
            for item in v:
                if isinstance(item, dict):
                    resolved_list.append(resolve_params(item, input_data))
                elif isinstance(item, str):
                    val = item
                    for key, input_val in input_data.items():
                        val = val.replace(f"{{{{{key}}}}}", str(input_val))
                    resolved_list.append(val)
                else:
                    resolved_list.append(item)
            resolved[k] = resolved_list
        else:
            resolved[k] = v
    return resolved

def execute_graph(node_id, nodes, global_context, results):
    if not node_id or str(node_id) not in nodes:
        return
        
    node = nodes[str(node_id)]
    tool_id = node.get("name")
    data = node.get("data", {})
    
    # Resolve parameters
    resolved_params = resolve_params(data, global_context)
    output_data = None
    
    if tool_id == "logic_if":
        cond_str = resolved_params.get("condition", "").strip()
        try:
            # Simple eval for conditions like: "'success' == 'success'" or "True"
            cond_val = eval(cond_str)
        except:
            cond_val = False
            
        output_route = "output_1" if cond_val else "output_2"
        outputs = node.get("outputs", {})
        route_conns = outputs.get(output_route, {}).get("connections", [])
        for conn in route_conns:
            execute_graph(conn.get("node"), nodes, global_context, results)
        return
        
    elif tool_id == "logic_loop":
        array_str = resolved_params.get("array_var")
        try:
            if isinstance(array_str, str):
                import ast
                arr = ast.literal_eval(array_str)
            else:
                arr = array_str
        except:
            arr = []
            
        if isinstance(arr, list):
            for item in arr:
                global_context["loop_item"] = item
                outputs = node.get("outputs", {})
                for out_key, out_val in outputs.items():
                    for conn in out_val.get("connections", []):
                        execute_graph(conn.get("node"), nodes, global_context, results)
        return
        
    elif tool_id.startswith("trigger_"):
        output_data = "Triggered"
        
    elif tool_id == "data_table":
        output_data = "Data manipulation completed"
        results.append({"tool": tool_id, "status": "success", "output": output_data})
        
    else:
        # Execute registered tool
        if tool_id in TOOL_REGISTRY:
            funcs = TOOL_REGISTRY[tool_id]["functions"]
            if funcs:
                try:
                    output_data = funcs[0](**resolved_params)
                    results.append({"tool": tool_id, "status": "success", "output": str(output_data)})
                except Exception as e:
                    output_data = f"Error: {e}"
                    results.append({"tool": tool_id, "status": "failed", "output": output_data})
                    
    # Save output to context for downstream nodes using node ID
    global_context[f"{node_id}_output"] = output_data
    
    # Traverse standard next nodes
    outputs = node.get("outputs", {})
    for out_key, out_val in outputs.items():
        for conn in out_val.get("connections", []):
            execute_graph(conn.get("node"), nodes, global_context, results)


def execute_workflow_from_canvas(canvas_data: dict, global_context: dict, results: list):
    """Execute workflow from our custom canvas format: {nodes: {}, connections: []}"""
    nodes = canvas_data.get("nodes", {})
    connections = canvas_data.get("connections", [])

    # Build adjacency list from connections
    adj = {nid: [] for nid in nodes}
    for conn in connections:
        frm = conn.get("from")
        to = conn.get("to")
        if frm in adj:
            adj[frm].append(to)

    # Find trigger nodes
    trigger_ids = [nid for nid, nd in nodes.items() if nd.get("type", "").startswith("trigger_")]
    
    visited = set()

    def visit(nid):
        if nid in visited or nid not in nodes:
            return
        visited.add(nid)
        nd = nodes[nid]
        node_type = nd.get("type", "")
        data = nd.get("data", {})
        resolved = resolve_params(data, global_context)
        output_data = None

        if node_type.startswith("trigger_"):
            output_data = "Triggered"
        elif node_type == "logic_if":
            cond_str = resolved.get("condition", "").strip()
            try:
                cond_val = eval(cond_str)
            except:
                cond_val = False
            # Only follow relevant branch
            branch_nodes = adj.get(nid, [])
            if branch_nodes:
                branch_target = branch_nodes[0] if cond_val else (branch_nodes[1] if len(branch_nodes) > 1 else None)
                if branch_target:
                    visit(branch_target)
            return
        elif node_type == "logic_loop":
            array_str = resolved.get("array_var")
            try:
                import ast
                arr = ast.literal_eval(array_str) if isinstance(array_str, str) else array_str
            except:
                arr = []
            if isinstance(arr, list):
                for item in arr:
                    global_context["loop_item"] = item
                    for next_id in adj.get(nid, []):
                        visit(next_id)
            return
        elif node_type == "data_table":
            output_data = "Data manipulation completed"
            results.append({"tool": node_type, "status": "success", "output": output_data})
        elif node_type == "ai_agent":
            try:
                agent_id = resolved.get("agent_id")
                query = resolved.get("query")
                if not agent_id or not query:
                    raise Exception("Agent ID and query are required.")
                
                from database import get_agent, current_user_id
                user_id = current_user_id.get()
                agent = get_agent(user_id, agent_id)
                if not agent:
                    raise Exception(f"Agent {agent_id} not found.")
                    
                from agent import run_agent_for_project
                user_id = current_user_id.get()
                output_data = run_agent_for_project(user_id=user_id, agent_id=agent_id, thread_id=0, prompt=query)
                results.append({"tool": node_type, "status": "success", "output": str(output_data)})
            except Exception as e:
                output_data = f"AI Agent error: {str(e)}"
                results.append({"tool": node_type, "status": "failed", "output": output_data})
        elif "::" in node_type:
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
                # --- END INTERCEPTION ---
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

        else:
            if node_type in TOOL_REGISTRY:
                funcs = TOOL_REGISTRY[node_type]["functions"]
                if funcs:
                    try:
                        output_data = funcs[0](**resolved)
                        results.append({"tool": node_type, "status": "success", "output": str(output_data)})
                    except Exception as e:
                        output_data = f"Error: {e}"
                        results.append({"tool": node_type, "status": "failed", "output": output_data})
            else:
                results.append({"tool": node_type, "status": "skipped", "output": f"Tool '{node_type}' not configured."})

        global_context[f"{nid}_output"] = output_data

        for next_id in adj.get(nid, []):
            visit(next_id)

    for t_id in trigger_ids:
        visit(t_id)

    # If no triggers found, just run all non-trigger nodes in order
    if not trigger_ids:
        for nid in nodes:
            visit(nid)


def execute_workflow(user_id: int, workflow_id: int, input_data: dict) -> dict:
    """Execute a workflow DAG."""
    token = current_user_id.set(user_id)
    try:
        workflow = get_workflow(user_id, workflow_id)
        if not workflow:
            return {"status": "error", "message": f"Workflow {workflow_id} not found."}

        steps = workflow.get("steps", {})
        results = []
        global_context = {**input_data}

        # Pre-load workflow variables into context
        if isinstance(steps, dict):
            for var in steps.get("variables", []):
                name = var.get("name", "").strip()
                val = var.get("value", "")
                if name:
                    global_context[name] = val

        if isinstance(steps, dict):
            linear_steps = None
            if "compiled_steps" in steps and "steps" in steps["compiled_steps"]:
                linear_steps = steps["compiled_steps"]["steps"]
            elif "canvas_data" in steps and "steps" in steps["canvas_data"]:
                linear_steps = steps["canvas_data"]["steps"]

            if linear_steps is not None and isinstance(linear_steps, list):
                for step in linear_steps:
                    step_id = step.get("id", "")
                    tool_id = step.get("type", "")
                    params = step.get("data", {})
                    resolved = resolve_params(params, global_context)
                    
                    assign_var = resolved.pop("assign_to_var", None)
                    
                    output_data = None
                    if tool_id.startswith("trigger_"):
                        output_data = "Triggered"
                        results.append({"tool": tool_id, "status": "success", "output": output_data})
                    elif tool_id == "ai_agent":
                        try:
                            agent_id = resolved.get("agent_id")
                            query = resolved.get("query")
                            if not agent_id or not query:
                                raise Exception("Agent ID and query are required.")
                                
                            from database import get_agent
                            agent = get_agent(user_id, agent_id)
                            if not agent:
                                raise Exception(f"Agent {agent_id} not found.")
                                
                            from agent import run_agent_for_project
                            output_data = run_agent_for_project(user_id=user_id, agent_id=agent_id, thread_id=0, prompt=query)
                            results.append({"tool": tool_id, "status": "success", "output": str(output_data)})
                        except Exception as e:
                            output_data = f"AI Agent error: {str(e)}"
                            results.append({"tool": tool_id, "status": "failed", "output": output_data})
                    elif tool_id in TOOL_REGISTRY:
                        funcs = TOOL_REGISTRY[tool_id]["functions"]
                        if funcs:
                            try:
                                output_data = funcs[0](**resolved)
                                results.append({"tool": tool_id, "status": "success", "output": str(output_data)})
                            except Exception as e:
                                output_data = f"Error: {e}"
                                results.append({"tool": tool_id, "status": "failed", "output": output_data})
                    else:
                        output_data = f"Tool '{tool_id}' not configured."
                        results.append({"tool": tool_id, "status": "skipped", "output": output_data})
                        
                    if step_id:
                        global_context[f"{step_id}_output"] = output_data
                    if assign_var:
                        global_context[assign_var] = output_data

            else:
                canvas_data = steps.get("canvas_data")
                if canvas_data and isinstance(canvas_data, dict):
                    if "nodes" in canvas_data:
                        execute_workflow_from_canvas(canvas_data, global_context, results)
                    elif "drawflow" in canvas_data:
                        try:
                            nodes = canvas_data["drawflow"]["Home"]["data"]
                            trigger_ids = [n_id for n_id, n_data in nodes.items() if n_data.get("name", "").startswith("trigger_")]
                            for t_id in trigger_ids:
                                execute_graph(t_id, nodes, global_context, results)
                        except (KeyError, TypeError):
                            results.append({"status": "error", "message": "Invalid legacy canvas data."})
                else:
                    results.append({"status": "info", "message": "Workflow has no executable steps."})

        elif isinstance(steps, list):
            # Legacy pure array format
            for step in steps:
                tool_id = step.get("tool")
                params = step.get("params", {})
                resolved = resolve_params(params, global_context)
                if tool_id in TOOL_REGISTRY:
                    funcs = TOOL_REGISTRY[tool_id]["functions"]
                    if funcs:
                        try:
                            out = funcs[0](**resolved)
                            results.append({"tool": tool_id, "status": "success", "output": str(out)})
                        except Exception as e:
                            results.append({"tool": tool_id, "status": "failed", "output": str(e)})

        return {
            "status": "completed",
            "workflow_name": workflow["name"],
            "results": results
        }
    finally:
        current_user_id.reset(token)

