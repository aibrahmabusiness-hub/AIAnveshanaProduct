import re

db_filepath = r"c:\Users\Admin\Documents\Agentic AI\backend\database.py"

with open(db_filepath, "r", encoding="utf-8") as f:
    db_content = f.read()

# 1. Add update_workflow_status
new_func = """def update_workflow_status(user_id, workflow_id, status):
    conn = get_conn()
    
    # Verify ownership
    cur = _execute(conn, 'SELECT id FROM workflows WHERE id = ? AND user_id = ?', (workflow_id, user_id))
    if not cur.fetchone():
        conn.close()
        raise PermissionError("User does not own this workflow")
        
    if USE_POSTGRES:
        _execute(conn, 'UPDATE workflows SET status = %s WHERE id = %s', (status, workflow_id))
    else:
        _execute(conn, 'UPDATE workflows SET status = ? WHERE id = ?', (status, workflow_id))
    conn.commit()
    conn.close()
    return {"id": workflow_id, "status": status}

def update_workflow_run"""

if "def update_workflow_status" not in db_content:
    db_content = db_content.replace("def update_workflow_run", new_func)

    with open(db_filepath, "w", encoding="utf-8") as f:
        f.write(db_content)
    print("database.py updated successfully.")


# 2. Update main.py
main_filepath = r"c:\Users\Admin\Documents\Agentic AI\backend\main.py"

with open(main_filepath, "r", encoding="utf-8") as f:
    main_content = f.read()

# Add PUT /api/workflows/{workflow_id}/status
status_api = """@app.put("/api/workflows/{workflow_id}/status")
async def api_update_workflow_status(workflow_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    data = await request.json()
    status = data.get("status")
    from database import update_workflow_status
    try:
        update_workflow_status(current_user["user_id"], workflow_id, status)
        reload_workflow_schedule(workflow_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/workflows/{workflow_id}")"""

if "@app.put(\"/api/workflows/{workflow_id}/status\")" not in main_content:
    main_content = main_content.replace('@app.delete("/api/workflows/{workflow_id}")', status_api)


# Update POST /api/workflows/{workflow_id}/execute to check status
old_execute = """@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    data = await request.json()"""

new_execute = """@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    if str(workflow_id) != "new_workflow":
        wf = get_workflow(current_user["user_id"], int(workflow_id))
        if wf and wf.get("status") == "inactive":
            raise HTTPException(status_code=400, detail="Cannot execute inactive workflow")

    data = await request.json()"""

if "wf.get(\"status\") == \"inactive\":" not in main_content:
    main_content = main_content.replace(old_execute, new_execute)

with open(main_filepath, "w", encoding="utf-8") as f:
    f.write(main_content)
print("main.py updated successfully.")
