import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas import WorkflowSchema, get_node_catalog, get_piece_schema, get_all_piece_schemas
from tasks import execute_workflow_task
from db import init_db, get_execution_history
import redis.asyncio as aioredis

REDIS_URL = "redis://localhost:6379/0"

app = FastAPI(title="Ultra-Lightweight Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/workflows/execute")
async def execute_workflow(workflow: WorkflowSchema):
    """Dispatch workflow execution to the Celery worker."""
    wf_dict = workflow.model_dump()
    task = execute_workflow_task.delay(wf_dict)
    return {"task_id": task.id, "status": "dispatched"}

@app.get("/api/nodes/schema")
async def get_nodes_schema():
    """Return node definitions and configuration schema metadata."""
    return {"nodes": get_node_catalog()}

@app.get("/api/nodes/schema/{piece_name}")
async def get_node_schema(piece_name: str):
    """Return JSON schema for a specific piece configuration."""
    schema = get_piece_schema(piece_name)
    if not schema:
        return {"error": f"Piece '{piece_name}' not found"}
    return {"piece_name": piece_name, "schema": schema}

@app.get("/api/nodes/all-schemas")
async def get_all_node_schemas():
    """Return all piece schemas with their definitions."""
    return {"schemas": get_all_piece_schemas()}

@app.get("/api/history")
async def history():
    """Return stored workflow execution history."""
    return get_execution_history()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    """Stream workflow execution logs from Redis pub/sub to WebSocket clients."""
    await websocket.accept()
    redis_client = aioredis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("workflow_logs")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                await asyncio.sleep(0.05)
                continue

            if message["type"] != "message":
                continue

            data = message["data"]
            if isinstance(data, bytes):
                data = data.decode()

            await websocket.send_text(data)

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("workflow_logs")
        await pubsub.close()
        await redis_client.close()

# Serve React static files
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
else:
    print(f"Warning: Frontend dist not found at {FRONTEND_DIST}")
    print("Build frontend: cd v2/frontend && npm run build")
