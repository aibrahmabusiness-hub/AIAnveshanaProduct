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

def execute_workflow(user_id: int, workflow_id: int, input_data: dict) -> dict:
    """Execute a workflow step-by-step."""
    # Set the current user context so that tool functions retrieve the correct credentials
    token = current_user_id.set(user_id)
    
    try:
        workflow = get_workflow(user_id, workflow_id)
        if not workflow:
            return {"status": "error", "message": f"Workflow {workflow_id} not found or access denied."}
        
        steps = workflow.get("steps", [])
        # Ensure steps are sorted by order
        steps = sorted(steps, key=lambda s: s.get("order", 0))
        
        results = []
        for step in steps:
            tool_id = step.get("tool")
            params = step.get("params", {})
            
            # Resolve parameters from input_data and accumulated results
            combined_context = {**input_data}
            for idx, res in enumerate(results):
                combined_context[f"step_{idx+1}_output"] = res.get("output", "")
            
            resolved_params = resolve_params(params, combined_context)
            
            # Find the registered function in tool registry
            if tool_id not in TOOL_REGISTRY:
                results.append({
                    "step": step.get("order"),
                    "tool": tool_id,
                    "status": "failed",
                    "output": f"Tool {tool_id} not registered."
                })
                continue
                
            funcs = TOOL_REGISTRY[tool_id]["functions"]
            if not funcs:
                results.append({
                    "step": step.get("order"),
                    "tool": tool_id,
                    "status": "failed",
                    "output": f"No execution functions defined for tool {tool_id}."
                })
                continue
            
            func = funcs[0]
            try:
                # Call function with resolved parameters
                # Inspect params to match signature if needed, but standard kwargs is fine
                output = func(**resolved_params)
                results.append({
                    "step": step.get("order"),
                    "tool": tool_id,
                    "status": "success",
                    "output": str(output)
                })
            except Exception as e:
                results.append({
                    "step": step.get("order"),
                    "tool": tool_id,
                    "status": "failed",
                    "output": f"Execution error: {str(e)}"
                })
                
        return {
            "status": "completed",
            "workflow_name": workflow["name"],
            "results": results
        }
        
    finally:
        current_user_id.reset(token)
