class WorkflowCreateRequest(BaseModel):
    agent_id: int
    name: str
    steps: Union[List[Any], Dict[str, Any]]
    status: str = "draft"


# --- Auth Endpoints ---

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # Check if user exists
    existing = get_user_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    pwd_hash = hash_password(request.password)
    user = create_user(request.username, request.email, pwd_hash)
    return {"status": "success", "user": {"username": user["username"], "email": user["email"]}}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user = get_user_by_username(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    orgs = get_user_organizations(user["id"])
    if not orgs:
        raise HTTPException(status_code=403, detail="User does not belong to any organization")
        
    default_org = orgs[0]
    token = create_access_token({
        "user_id": user["id"], 
        "username": user["username"], 
        "role": default_org["role"],
        "organization_id": default_org["id"]
    })
    
    return {
        "status": "success", 
        "access_token": token, 
        "token_type": "bearer",
        "username": user["username"],
        "organization": default_org["name"]
    }

class WorkflowExecuteRequest(BaseModel):
    input_data: dict
    steps: list = []

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

@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: WorkflowExecuteRequest, current_user: dict = Depends(get_current_user)):
    # Proxy to lightweight engine
    import httpx
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post("http://localhost:3001/execute_workflow", json={
                "steps": request.steps,
                "initialData": request.input_data
            })
            return res.json()
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return {"success": False, "error": str(e)}



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

