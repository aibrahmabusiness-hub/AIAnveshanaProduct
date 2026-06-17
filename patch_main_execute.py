import re
with open(r"C:\Users\Admin\Documents\Agentic AI\backend\main.py", "r", encoding="utf-8") as f:
    js = f.read()

new_func = """class WorkflowExecuteRequest(BaseModel):
    input_data: dict
    steps: list = []

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
"""

js = re.sub(r'class WorkflowExecuteRequest.*?return res', new_func, js, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\backend\main.py", "w", encoding="utf-8") as f:
    f.write(js)
