import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\backend\main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add WebSocket imports
if 'from fastapi import' in content and 'WebSocket' not in content:
    content = content.replace('from fastapi import FastAPI, Depends', 'from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks')

# Add WebSocket manager
ws_code = """
# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        import json
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
"""

if 'class ConnectionManager' not in content:
    content = content.replace('# --- Health ---', ws_code + '\n# --- Health ---')

# Replace run_workflow
old_run = """@app.post("/api/workflows/{workflow_id}/execute")
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
        return {"success": False, "error": str(e)}"""

new_run = """import uuid
import asyncio

async def background_workflow_execution(workflow_id: str, payload: dict, token: str):
    task_id = payload["task_id"]
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    variables = payload.get("variables", [])
    
    await manager.broadcast({
        "type": "workflow_start",
        "data": {"workflow_id": workflow_id, "task_id": task_id}
    })
    
    import httpx
    try:
        headers = {}
        if token:
            headers["Authorization"] = token
            
        initial_data = {}
        for v in variables:
            initial_data[v.get("name")] = v.get("value")
            
        # Very simple sequential execution simulating lightweight engine format
        # In a real DAG we'd sort topologically, but for now we'll just run nodes that aren't triggers
        # Or even better, we can just pass the whole DAG to execute_workflow_from_canvas in workflows.py!
        # But we need to yield to the event loop.
        
        from workflows import execute_workflow_from_canvas
        results = []
        global_context = {**initial_data}
        
        # We execute it synchronously but emit a start and end
        canvas_data = {"nodes": {n["id"]: n for n in nodes}, "connections": edges}
        
        # We don't have websocket events per-node if we use the synchronous execute_workflow_from_canvas,
        # but the UI will recover and see the final result.
        # Alternatively, we just map it to the lightweight engine
        
        steps = []
        # sort nodes by x position as a proxy for execution order if DAG fails
        nodes.sort(key=lambda n: n.get("position", {}).get("x", 0))
        for n in nodes:
            if n.get("type", "").startswith("trigger_"):
                continue
            config = n.get("data", {}).get("config", {})
            piece_name = n.get("data", {}).get("piece", "core")
            action_name = n.get("data", {}).get("action", "")
            steps.append({
                "id": n["id"],
                "type": f"{piece_name}::{action_name}",
                "data": config
            })
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post("http://127.0.0.1:3001/execute_workflow", json={
                "steps": steps,
                "initialData": initial_data
            }, headers=headers)
            
            data = res.json()
            logs = data.get("logs", [])
            for log in logs:
                success = log.get("success", False)
                await manager.broadcast({
                    "type": "node_finished",
                    "data": {
                        "workflow_id": workflow_id,
                        "task_id": task_id,
                        "node_id": log.get("step"),
                        "status": "success" if success else "failed",
                        "result": log.get("result", ""),
                        "error": log.get("error", "")
                    }
                })
        
        await manager.broadcast({
            "type": "workflow_finished",
            "data": {"workflow_id": workflow_id, "task_id": task_id, "status": "success"}
        })
    except Exception as e:
        await manager.broadcast({
            "type": "workflow_error",
            "data": {"workflow_id": workflow_id, "task_id": task_id, "error": str(e)}
        })


@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    data = await request.json()
    task_id = str(uuid.uuid4())
    data["task_id"] = task_id
    token = request.headers.get("authorization")
    
    background_tasks.add_task(background_workflow_execution, workflow_id, data, token)
    return {"task_id": task_id, "status": "dispatched"}
"""

if old_run in content:
    content = content.replace(old_run, new_run)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
