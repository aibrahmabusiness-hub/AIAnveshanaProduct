import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from schemas import WorkflowSchema, get_node_catalog
from tasks import execute_workflow_task
from db import init_db, get_execution_history

app = FastAPI(title="Ultra-Lightweight Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory WebSocket connections for testing
active_connections = []

# In-memory user store for testing
users_db = {
    "test": "test123"
}

# In-memory projects store
projects_db = {
    "1": {"id": "1", "name": "Sample Project", "nodes": [], "edges": [], "created_at": "2024-01-01"}
}
next_project_id = 2

# Pydantic models for auth
class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str

class CreateProjectRequest(BaseModel):
    name: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """Authenticate user and return tokens."""
    if req.username in users_db and users_db[req.username] == req.password:
        return {
            "access_token": f"token_{req.username}",
            "ap_token": f"ap_token_{req.username}",
            "ap_projectId": "default_project",
            "username": req.username
        }
    return {"error": "Invalid credentials"}, 401

@app.post("/api/auth/register")
async def register(req: SignupRequest):
    """Register new user."""
    if req.username in users_db:
        return {"error": "User already exists"}, 400
    users_db[req.username] = req.password
    return {"message": "User created", "username": req.username}

@app.get("/api/agents")
async def get_agents():
    """Return list of projects."""
    return list(projects_db.values())

@app.post("/api/agents")
async def create_agent(req: CreateProjectRequest):
    """Create a new project."""
    global next_project_id
    project_id = str(next_project_id)
    next_project_id += 1
    
    new_project = {
        "id": project_id,
        "name": req.name,
        "nodes": [],
        "edges": [],
        "created_at": "2024-01-01"
    }
    projects_db[project_id] = new_project
    return new_project

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Return project details."""
    if agent_id in projects_db:
        return projects_db[agent_id]
    return {"error": "Project not found"}, 404

@app.post("/api/workflows/execute")
async def execute_workflow(workflow: WorkflowSchema):
    """Dispatch workflow execution to Celery (requires Redis)."""
    wf_dict = workflow.model_dump()
    try:
        task = execute_workflow_task.delay(wf_dict)
        return {"task_id": task.id, "status": "dispatched"}
    except Exception as e:
        return {"status": "error", "message": "Celery not available. Make sure Redis is running."}

@app.get("/api/nodes/schema")
async def get_nodes_schema():
    """Return node definitions and configuration schema metadata."""
    return {"nodes": get_node_catalog()}

@app.get("/api/history")
async def history():
    """Return stored workflow execution history."""
    return get_execution_history()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/workflows/{workflow_id}")
async def save_workflow(workflow_id: str, workflow: WorkflowSchema):
    """Save workflow configuration."""
    return {"message": "Workflow saved", "id": workflow_id}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for logs (simplified - no Redis)."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Serve React static files
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
else:
    print(f"WARNING: Frontend dist not found at {FRONTEND_DIST}")
    print("Build frontend first: cd v2/frontend && npm run build")
    print("Or run in dev mode on port 5173: npm run dev")
