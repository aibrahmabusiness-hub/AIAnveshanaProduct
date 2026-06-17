import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_workflows_code = '''
class WorkflowCreateRequest(BaseModel):
    agent_id: int
    name: str
    steps: Union[List[Any], Dict[str, Any]]
    status: str = "draft"

@app.post("/api/workflows")
async def api_create_workflow(workflow: WorkflowCreateRequest, current_user: dict = Depends(get_current_user)):
    try:
        wf_id = create_workflow(current_user["id"], workflow.agent_id, workflow.name, workflow.steps, workflow.status)
        return {"success": True, "workflow_id": wf_id}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows")
async def api_get_workflows(agent_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    try:
        workflows = get_workflows(current_user["id"], agent_id)
        return {"success": True, "workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/{workflow_id}")
async def api_get_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    wf = get_workflow(current_user["id"], workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True, "workflow": wf}

@app.put("/api/workflows/{workflow_id}")
async def api_update_workflow(workflow_id: int, workflow: WorkflowCreateRequest, current_user: dict = Depends(get_current_user)):
    from database import _execute, get_conn
    conn = get_conn()
    import json
    steps_str = json.dumps(workflow.steps) if isinstance(workflow.steps, (dict, list)) else workflow.steps
    try:
        cur = _execute(conn, 'UPDATE workflows SET name = %s, steps = %s, status = %s WHERE id = %s AND user_id = %s',
                      (workflow.name, steps_str, workflow.status, workflow_id, current_user["id"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"success": True}

@app.delete("/api/workflows/{workflow_id}")
async def api_delete_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    try:
        delete_workflow(current_user["id"], workflow_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CredentialRequest(BaseModel):
    tool_name: str
    credentials: dict

@app.get("/api/credentials")
async def api_get_credentials(current_user: dict = Depends(get_current_user)):
    try:
        creds = get_all_credentials(current_user["id"])
        return {"success": True, "credentials": creds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credentials")
async def api_save_credentials(req: CredentialRequest, current_user: dict = Depends(get_current_user)):
    try:
        save_credentials(current_user["id"], req.tool_name, req.credentials)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/credentials/{tool_name}")
async def api_delete_credentials(tool_name: str, current_user: dict = Depends(get_current_user)):
    try:
        delete_credentials(current_user["id"], tool_name)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

# We will replace the OLD workflows endpoints with the NEW ones, and append the credentials endpoints.
# Let's find the Workflows Endpoints section and replace it entirely up to # --- Health ---
old_workflows_pattern = r'# --- Workflows Endpoints ---.*?# --- Health ---'
if re.search(old_workflows_pattern, content, re.DOTALL):
    content = re.sub(old_workflows_pattern, '# --- Workflows Endpoints ---\n\n' + new_workflows_code + '\n\n# --- Health ---', content, flags=re.DOTALL)
else:
    # If not found, just insert before Health
    content = content.replace('# --- Health ---', '# --- Workflows Endpoints ---\n\n' + new_workflows_code + '\n\n# --- Health ---')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
