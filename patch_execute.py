import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

execute_code = '''
class WorkflowExecuteRequest(BaseModel):
    input_data: dict
    steps: list = []

@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: int, request: WorkflowExecuteRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    res = execute_workflow(user_id, workflow_id, request.input_data)
    return res
'''
content = content.replace('# --- Health ---', execute_code + '\n# --- Health ---')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
