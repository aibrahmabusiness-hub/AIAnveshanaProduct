import sys
import os

js_path = r"c:\Users\Admin\Documents\Agentic AI\frontend\project.js"
py_path = r"c:\Users\Admin\Documents\Agentic AI\backend\main.py"

# 1. Patch Python backend
with open(py_path, "r", encoding="utf-8") as f:
    py_content = f.read()

old_py = """@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    if str(workflow_id) != "new_workflow":
        wf = get_workflow(current_user["user_id"], int(workflow_id))
        if wf and wf.get("status") != "active":
            raise HTTPException(status_code=400, detail="Cannot execute inactive workflow")

    data = await request.json()"""

new_py = """@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    data = await request.json()
    is_test = data.get("is_test", False)

    if str(workflow_id) != "new_workflow" and not is_test:
        wf = get_workflow(current_user["user_id"], int(workflow_id))
        if wf and wf.get("status") != "active":
            raise HTTPException(status_code=400, detail="Cannot execute inactive workflow")
"""

if old_py in py_content:
    py_content = py_content.replace(old_py, new_py)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(py_content)
    print("Patched main.py successfully.")

# 2. Patch Javascript frontend
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

old_js = """            const res = await authFetch(`/api/workflows/${flowId}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input_data: inputData,
                    steps: stepsArray
                })
            });"""

new_js = """            const res = await authFetch(`/api/workflows/${flowId}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input_data: inputData,
                    steps: stepsArray,
                    is_test: true
                })
            });"""

if old_js in js_content:
    js_content = js_content.replace(old_js, new_js)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("Patched project.js successfully.")
