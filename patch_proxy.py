import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

execute_code_new = '''
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
        return {"success": False, "error": str(e)}
'''

# Find the old run_workflow and replace it
pattern = r'@app\.post\("/api/workflows/\{workflow_id\}/execute"\).*?return res\n'
content = re.sub(pattern, execute_code_new.strip() + '\n', content, flags=re.DOTALL)

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
