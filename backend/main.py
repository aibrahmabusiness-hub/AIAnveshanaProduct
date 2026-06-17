import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, List, Union, Dict, Any

from agent import run_agent_for_project
from database import (
    init_db, create_agent, get_all_agents, get_agent, update_agent_tools,
    add_knowledge, get_knowledge, delete_knowledge, get_chat_history,
    save_credentials, get_credentials, create_user, get_user_by_username,
    add_llm_config, get_all_llm_configs, set_default_llm_config, delete_llm_config, update_agent_llm,
    create_workflow, get_workflows, get_workflow, delete_workflow,
    create_chat_thread, get_chat_threads, get_chat_thread, delete_chat_thread,
    update_agent, add_chat_message, delete_agent, set_default_agent,
    get_tool_connections, save_tool_connection, delete_tool_connection, current_connection_id, current_user_id,
    get_all_credentials, delete_credentials
)
from auth import hash_password, verify_password, create_access_token, get_current_user
from vector_store import add_to_vector_store, delete_from_vector_store
from workflows import execute_workflow
from tools.tool_registry import get_available_tools
from scheduler import scheduler, load_all_schedules, reload_workflow_schedule

app = FastAPI(title="AI Anveshana Platform")

@app.on_event("startup")
async def startup_event():
    scheduler.start()
    load_all_schedules()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if path.startswith("/static") or path.endswith(".js") or path.endswith(".css") or "project.js" in path:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
# Structured logging for production
import logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("anveshana")

# Initialize the database on startup
init_db()
logger.info("Database initialized successfully")

# --- Health Check ---

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring, load balancers, and container probes."""
    import datetime
    return {
        "status": "ok",
        "service": "anveshana-ai",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


# --- Request Models ---

class RegisterRequest(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AgentRequest(BaseModel):
    project_id: int
    name: str
    description: str
    system_prompt: str = ""
    connected_tools: list = []

class UpdateAgentRequest(BaseModel):
    name: str
    description: str
    system_prompt: str = ""
    user_prompt: str = ""
    creativity: float = 0.5
    guardrails: bool = True
    max_tool_calls: int = 80
    llm_config_id: Optional[int] = None
    guardrail_types: List[str] = []

class ChatRequest(BaseModel):
    prompt: str

class ThreadRequest(BaseModel):
    agent_id: Optional[int] = None
    project_id: int
    title: str

class CredentialRequest(BaseModel):
    tool_name: str
    credentials: dict

class UpdateToolsRequest(BaseModel):
    connected_tools: list

class LLMConfigRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str
    project_id: Optional[int] = None

class LLMTestRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str

class CredentialTestRequest(BaseModel):
    tool_name: str
    credentials: dict

class AgentLLMRequest(BaseModel):
    llm_config_id: Optional[int] = None

class DefaultAgentRequest(BaseModel):
    project_id: int

class WorkflowRequest(BaseModel):
    agent_id: int
    name: str
    steps: list

class WorkflowExecuteRequest(BaseModel):
    input_data: dict

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
    
    token = create_access_token({"user_id": user["id"], "username": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "user_id": user["id"]
    }

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# --- Agent Endpoints ---


class GenerateAgentRequest(BaseModel):
    project_id: int
    intent: str

@app.post("/api/agents/generate_from_prompt")
async def generate_agent_from_prompt(request: GenerateAgentRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # 1. Call Mistral
    import httpx
    import json
    MISTRAL_API_KEY = "xkHphgru9SSK7ybzC5BIHwCRnoBXJeha"
    MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

    system_msg = """You are an expert AI agent architect. 
The user will describe an agent they need.
Generate a comprehensive system prompt for this agent.
The system prompt must be structured with these explicit sections:
- Role
- Goal
- Actions
- Result

Provide a concise, professional 'name' for the agent, and a brief 'description'.
Return ONLY a valid JSON object matching this exact schema, with no markdown formatting outside the JSON:
{
  "name": "Agent Name",
  "description": "Short description",
  "system_prompt": "Role: ...\\n\\nGoal: ...\\n\\nActions: ...\\n\\nResult: ..."
}
Make SURE to use explicit "\\n\\n" newline characters to separate the Role, Goal, Actions, and Result sections inside the system_prompt string, so it formats nicely in a text box.
"""

    payload = {
        "model": "open-mixtral-8x7b",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": request.intent}
        ],
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(MISTRAL_URL, headers=headers, json=payload, timeout=45.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Mistral API error: {resp.text}")
            
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            name = parsed.get("name", "Custom Agent")
            desc = parsed.get("description", "Agent generated from prompt")
            sys_prompt = parsed.get("system_prompt", "")
            
            # 2. Create the agent in DB
            from database import create_agent
            agent = create_agent(
                user_id=user_id,
                project_id=request.project_id,
                name=name,
                description=desc,
                system_prompt=sys_prompt,
                user_prompt="",
                creativity=0.5,
                guardrails=True,
                max_tool_calls=80,
                connected_tools=[]
            )
            return {"status": "success", "agent": agent}
            
    except Exception as e:
        print("Error generating agent:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return {"agents": get_all_agents(user_id)}

@app.post("/api/agents")
async def create_new_agent(request: AgentRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    new_agent = create_agent(user_id, request.project_id, request.name, request.description, request.system_prompt, request.connected_tools)
    return new_agent

@app.get("/api/agents/{agent_id}")
async def get_single_agent(agent_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    agent = get_agent(user_id, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/api/agents/{agent_id}")
async def update_agent_details(agent_id: int, request: UpdateAgentRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    update_agent(
        user_id, agent_id, request.name, request.description,
        request.system_prompt, request.user_prompt, request.creativity,
        request.guardrails, request.max_tool_calls, request.llm_config_id,
        request.guardrail_types
    )
    return {"status": "success"}

@app.put("/api/agents/{agent_id}/tools")
async def update_tools(agent_id: int, request: UpdateToolsRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    update_agent_tools(user_id, agent_id, request.connected_tools)
    return {"status": "updated"}

@app.put("/api/agents/{agent_id}/llm")
async def update_agent_llm_config(agent_id: int, request: AgentLLMRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    update_agent_llm(user_id, agent_id, request.llm_config_id)
    return {"status": "updated"}

@app.put("/api/agents/{agent_id}/default")
async def set_agent_default_endpoint(agent_id: int, request: DefaultAgentRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        set_default_agent(user_id, request.project_id, agent_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/agents/{agent_id}")
async def delete_agent_endpoint(agent_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    agent = get_agent(user_id, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 1. Clean up knowledge base docs from vector store
    kb_docs = get_knowledge(user_id, agent_id)
    for doc in kb_docs:
        try:
            delete_from_vector_store(doc["id"])
        except Exception as e:
            logger.error(f"Error deleting doc {doc['id']} from vector store: {e}")
            
    # 2. Delete agent from database (cascades)
    delete_agent(user_id, agent_id)
    return {"status": "deleted"}

# --- Chat Endpoints (Threaded) ---

@app.post("/api/chat/threads")
async def create_new_thread(request: ThreadRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        thread = create_chat_thread(user_id, request.agent_id, request.title, request.project_id)
        return thread
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")

@app.get("/api/chat/threads")
async def list_threads(project_id: int, agent_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    threads = get_chat_threads(user_id, agent_id, project_id)
    return {"threads": threads}

@app.delete("/api/chat/threads/{thread_id}")
async def remove_thread(thread_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        delete_chat_thread(user_id, thread_id)
        return {"status": "deleted"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")

@app.get("/api/chat/threads/{thread_id}/history")
async def get_thread_chat_history(thread_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    history = get_chat_history(user_id, thread_id)
    return {"history": history}

@app.post("/api/chat/threads/{thread_id}/message")
async def send_thread_message(thread_id: int, request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Verify thread ownership and lookup agent_id
    thread = get_chat_thread(user_id, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found or access denied")
        
    agent_id = thread["agent_id"]
    
    # Save user message immediately to database to preserve chronological order
    add_chat_message(user_id, thread_id, "user", request.prompt)
    
    import queue
    import threading
    import json
    
    q = queue.Queue()
    
    def on_stage(stage: str, tool_name: str = None):
        q.put({"type": "stage", "stage": stage, "tool": tool_name})
        try:
            # Save stage progress message into database
            add_chat_message(user_id, thread_id, "stage", json.dumps({"stage": stage, "tool": tool_name}))
        except Exception as e:
            print(f"[Main] Error saving stage to database: {e}")
        
    def worker():
        try:
            reply = run_agent_for_project(user_id, agent_id, thread_id, request.prompt, on_stage_change=on_stage)
            q.put({"type": "reply", "reply": reply})
        except Exception as e:
            q.put({"type": "error", "message": str(e)})
        finally:
            q.put(None)
            
    threading.Thread(target=worker, daemon=True).start()
    
    def event_generator():
        while True:
            item = q.get()
            if item is None:
                break
            yield json.dumps(item) + "\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Knowledge Base Endpoints ---

@app.get("/api/knowledge/{agent_id}")
async def list_knowledge(agent_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    docs = get_knowledge(user_id, agent_id)
    return {"documents": docs}

def process_knowledge_file(agent_id: int, doc_id: int, filename: str, text_content: str):
    from database import update_knowledge_status
    try:
        add_to_vector_store(agent_id, doc_id, filename, text_content)
        update_knowledge_status(doc_id, "synced")
    except Exception as e:
        print(f"[Main] Vector store insert error: {e}")
        update_knowledge_status(doc_id, "failed")

@app.post("/api/knowledge/{agent_id}")
async def upload_knowledge(agent_id: int, background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    
    # Save to database with status 'processing'
    doc = add_knowledge(user_id, agent_id, file.filename, text_content)
    
    # Add to vector store asynchronously
    background_tasks.add_task(process_knowledge_file, agent_id, doc["id"], file.filename, text_content)
        
    return doc

@app.post("/api/knowledge/{agent_id}/sync/{doc_id}")
async def sync_knowledge(agent_id: int, doc_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    from database import get_knowledge_content_by_id, update_knowledge_status
    
    # Fetch content and verify ownership
    try:
        doc_info = get_knowledge_content_by_id(user_id, doc_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # Update status back to processing
    update_knowledge_status(doc_id, "processing")
    
    # Re-queue background task
    background_tasks.add_task(process_knowledge_file, agent_id, doc_id, doc_info["filename"], doc_info["content"])
    
    return {"status": "processing"}

@app.delete("/api/knowledge/{kb_id}")
async def remove_knowledge(kb_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Remove from ChromaDB vector store
    delete_from_vector_store(kb_id)
    
    # Delete from database
    try:
        delete_knowledge(user_id, kb_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return {"status": "deleted"}

# --- Tools Endpoints ---

@app.get("/api/tools")
async def list_available_tools(current_user: dict = Depends(get_current_user)):
    return {"tools": get_available_tools()}

# --- Credentials Endpoints ---



def run_connection_test(tool_name: str, creds: dict) -> str:
    tool_name = tool_name.lower()
    if tool_name == "servicenow":
        instance_url = creds.get("instance_url", "").rstrip("/")
        username = creds.get("username")
        password = creds.get("password")
        client_id = creds.get("client_id")
        client_secret = creds.get("client_secret")
        
        if not instance_url or not username or not password:
            raise Exception("Missing instance URL, username, or password.")
            
        import requests
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        auth = None
        
        if client_id and client_secret:
            token_url = f"{instance_url}/oauth_token.do"
            token_payload = {
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password
            }
            token_res = requests.post(token_url, data=token_payload, timeout=8)
            if token_res.status_code == 200:
                token = token_res.json().get("access_token")
                headers["Authorization"] = f"Bearer {token}"
            else:
                auth = (username, password)
        else:
            auth = (username, password)
            
        test_url = f"{instance_url}/api/now/table/incident?sysparm_limit=1"
        res = requests.get(test_url, headers=headers, auth=auth, timeout=8)
        if res.status_code not in [200, 201]:
            raise Exception(f"ServiceNow returned HTTP {res.status_code}: {res.text}")
        return "Successfully connected to ServiceNow."
        
    elif tool_name == "salesforce":
        instance_url = creds.get("instance_url")
        username = creds.get("username")
        password = creds.get("password")
        security_token = creds.get("security_token")
        
        if not instance_url or not username or not password:
            raise Exception("Missing instance URL, username, or password.")
            
        from simple_salesforce import Salesforce
        domain = "login"
        if "test.salesforce.com" in instance_url:
            domain = "test"
        Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain
        )
        return "Successfully connected to Salesforce."
        
    elif tool_name == "gmail":
        username = creds.get("username")
        password = creds.get("password")
        
        if not username or not password:
            raise Exception("Missing Gmail email or App Password.")
            
        import smtplib
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=8)
        server.login(username, password)
        server.quit()
        return "Successfully connected to Gmail SMTP."
        
    elif tool_name == "jira":
        instance_url = creds.get("instance_url", "").rstrip("/")
        email = creds.get("username")
        api_token = creds.get("password")
        
        if not instance_url or not email or not api_token:
            raise Exception("Missing instance URL, email, or API token.")
            
        import requests
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        auth = (email, api_token)
        test_url = f"{instance_url}/rest/api/3/myself"
        
        res = requests.get(test_url, headers=headers, auth=auth, timeout=8)
        if res.status_code != 200:
            raise Exception(f"Jira returned HTTP {res.status_code}: {res.text}")
        return f"Successfully connected to Jira. User: {res.json().get('displayName', email)}"
        
    else:
        raise Exception(f"Unsupported tool: {tool_name}")

@app.post("/api/credentials/test")
async def test_tool_credentials(request: CredentialTestRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    tool_name = request.tool_name.lower()
    existing = get_credentials(user_id, tool_name) or {}
    creds = dict(request.credentials)
    for k, v in creds.items():
        if v == "********" and k in existing:
            creds[k] = existing[k]
    
    try:
        msg = run_connection_test(tool_name, creds)
        return {"status": "success", "message": msg}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

@app.get("/api/credentials/{tool_name}")
async def get_tool_credentials_status(tool_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    creds = get_credentials(user_id, tool_name)
    is_configured = bool(creds)
    safe_creds = {}
    for k, v in creds.items():
        if any(s in k.lower() for s in ["password", "secret", "token", "key"]):
            safe_creds[k] = "********" if v else ""
        else:
            safe_creds[k] = v
    return {"tool_name": tool_name, "configured": is_configured, "credentials": safe_creds}

# --- LLM Config Endpoints ---

@app.post("/api/settings/llm")
async def add_new_llm_config(request: LLMConfigRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    config = add_llm_config(user_id, request.provider, request.model_name, request.api_key, request.project_id)
    return config

@app.post("/api/settings/llm/test")
async def test_llm_connection(request: LLMTestRequest, current_user: dict = Depends(get_current_user)):
    provider = request.provider.lower()
    model = request.model_name
    key = request.api_key
    
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=key)
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content("Ping", generation_config={"max_output_tokens": 5})
            text = response.text
            return {"status": "success", "message": f"Successfully connected. Response: {text.strip()}"}
            
        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Ping"}],
                max_tokens=5
            )
            text = response.choices[0].message.content
            return {"status": "success", "message": f"Successfully connected. Response: {text.strip()}"}
            
        elif provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=key)
            response = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": "Ping"}],
                max_tokens=5
            )
            text = response.content[0].text
            return {"status": "success", "message": f"Successfully connected. Response: {text.strip()}"}
            
        elif provider == "mistral":
            import requests
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Ping"}],
                "max_tokens": 5
            }
            res = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=120)
            if res.status_code != 200:
                raise Exception(f"Mistral API returned status {res.status_code}: {res.text}")
            text = res.json()["choices"][0]["message"]["content"]
            return {"status": "success", "message": f"Successfully connected. Response: {text.strip()}"}
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

@app.get("/api/settings/llm")
async def list_llm_configs(project_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    configs = get_all_llm_configs(user_id, project_id)
    return {"configs": configs}

@app.post("/api/settings/llm/{config_id}/default")
async def set_default_config(config_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    set_default_llm_config(user_id, config_id)
    return {"status": "success"}

@app.delete("/api/settings/llm/{config_id}")
async def remove_llm_config(config_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    delete_llm_config(user_id, config_id)
    return {"status": "deleted"}

# --- Workflows Endpoints ---


class WorkflowCreateRequest(BaseModel):
    agent_id: Optional[int] = None
    project_id: Optional[int] = None
    name: str
    steps: Union[List[Any], Dict[str, Any]]
    status: str = "draft"

@app.post("/api/workflows")
async def api_create_workflow(workflow: WorkflowCreateRequest, current_user: dict = Depends(get_current_user)):
    try:
        wf_id = create_workflow(current_user["user_id"], workflow.agent_id, workflow.name, workflow.steps, workflow.status, workflow.project_id)
        parsed_id = wf_id["id"] if isinstance(wf_id, dict) else wf_id
        reload_workflow_schedule(parsed_id)
        return {"success": True, "workflow_id": parsed_id}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows")
async def api_get_workflows(project_id: int, agent_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    try:
        workflows = get_workflows(current_user["user_id"], agent_id, project_id)
        return {"success": True, "workflows": workflows}
    except Exception as e:
        import traceback
        print("Error getting workflows:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/runs")
async def api_get_workflow_runs(project_id: int, workflow_id: Optional[int] = None, status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    from database import get_workflow_runs
    try:
        runs = get_workflow_runs(current_user["user_id"], workflow_id, status, project_id)
        return {"success": True, "runs": runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/{workflow_id}")
async def api_get_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    wf = get_workflow(current_user["user_id"], workflow_id)
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
                      (workflow.name, steps_str, workflow.status, workflow_id, current_user["user_id"]))
        conn.commit()
        reload_workflow_schedule(workflow_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"success": True}

@app.put("/api/workflows/{workflow_id}/status")
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

@app.delete("/api/workflows/{workflow_id}")
async def api_delete_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    try:
        delete_workflow(current_user["user_id"], workflow_id)
        reload_workflow_schedule(workflow_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CredentialRequest(BaseModel):
    tool_name: str
    credentials: dict

@app.get("/api/credentials")
async def api_get_credentials(current_user: dict = Depends(get_current_user)):
    try:
        creds = get_all_credentials(current_user["user_id"])
        return {"success": True, "credentials": creds}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credentials")
async def api_save_credentials(req: CredentialRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        existing_connections = get_tool_connections(user_id, req.tool_name)
        
        if existing_connections:
            existing_conn = existing_connections[0]
            new_creds = dict(req.credentials)
            for k, v in new_creds.items():
                if v == "********" and k in existing_conn:
                    new_creds[k] = existing_conn[k]
            if "id" in existing_conn: new_creds["id"] = existing_conn["id"]
            if "name" in existing_conn: new_creds["name"] = existing_conn["name"]
            existing_connections[0] = new_creds
        else:
            new_creds = dict(req.credentials)
            new_creds["id"] = "default"
            new_creds["name"] = "Default Account"
            existing_connections = [new_creds]

        try:
            run_connection_test(req.tool_name, new_creds)
        except Exception as test_err:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {str(test_err)}")
            
        payload = {"connections": existing_connections}
        save_credentials(user_id, req.tool_name, payload)
        return {"success": True}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/credentials/{tool_name}")
async def api_delete_credentials(tool_name: str, current_user: dict = Depends(get_current_user)):
    try:
        delete_credentials(current_user["user_id"], tool_name)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/credentials/{tool_name}/accounts")
async def api_get_tool_connections(tool_name: str, current_user: dict = Depends(get_current_user)):
    try:
        connections = get_tool_connections(current_user["user_id"], tool_name)
        # Mask credentials before returning to UI
        safe_connections = []
        for conn in connections:
            safe_conn = {}
            for k, v in conn.items():
                if any(s in k.lower() for s in ["password", "secret", "token", "key"]):
                    safe_conn[k] = "********" if v else ""
                else:
                    safe_conn[k] = v
            safe_connections.append(safe_conn)
        return {"success": True, "connections": safe_connections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SaveConnectionRequest(BaseModel):
    id: Optional[str] = None
    name: str
    credentials: dict

@app.post("/api/credentials/{tool_name}/accounts")
async def api_save_tool_connection(tool_name: str, req: SaveConnectionRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        # Merge new credentials with existing if password masked
        existing_connections = get_tool_connections(user_id, tool_name)
        existing_conn = next((c for c in existing_connections if c.get("id") == req.id), None) if req.id else None
        
        creds = dict(req.credentials)
        if existing_conn:
            for k, v in creds.items():
                if v == "********" and k in existing_conn:
                    creds[k] = existing_conn[k]
                    
        # Verify credentials before saving
        try:
            run_connection_test(tool_name, creds)
        except Exception as test_err:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {str(test_err)}")
            
        connection_data = {
            "id": req.id,
            "name": req.name,
            **creds
        }
        saved = save_tool_connection(user_id, tool_name, connection_data)
        return {"success": True, "connection": saved}
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/credentials/{tool_name}/accounts/{connection_id}")
async def api_delete_tool_connection(tool_name: str, connection_id: str, current_user: dict = Depends(get_current_user)):
    try:
        delete_tool_connection(current_user["user_id"], tool_name, connection_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/execute")
async def execute_tool_action(req: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    tool_name = req.get("tool_name", "").lower()
    action_name = req.get("action_name", "")
    params = dict(req.get("params", {}))
    
    # Extract connection
    connection_id = params.pop("connection_id", None) or params.pop("connection", None)
    
    # Set the current connection in ContextVar
    token_conn = None
    if connection_id:
        token_conn = current_connection_id.set(connection_id)
        
    token_user = current_user_id.set(user_id)
        
    try:
        full_action = f"{tool_name}::{action_name}"
        from tools.tool_registry import TOOL_REGISTRY
        
        # Gmail
        if "gmail" in tool_name:
            from tools.gmail_tools import read_gmail_inbox, mark_gmail_read, send_gmail, search_gmail_inbox
            if action_name == "default" or "send" in action_name or "gmail_send" in action_name or "send" in tool_name:
                print(f"Executing send_gmail with params: {params}")
                to_val = params.get("to") or params.get("receiver") or params.get("email_to")
                subject_val = params.get("subject") or "No Subject"
                body_val = params.get("body") or ""
                if not to_val:
                    raise Exception("Missing recipient 'to' or 'receiver'")
                output = send_gmail(
                    to=to_val, 
                    subject=subject_val, 
                    body=body_val,
                    cc=params.get("cc"),
                    bcc=params.get("bcc"),
                    body_type=params.get("body_type", "plain_text"),
                    reply_to=params.get("reply_to"),
                    sender_name=params.get("sender_name"),
                    from_email=params.get("from_email") or params.get("from")
                )
                print(f"send_gmail output: {output}")
                return {"success": True, "output": output}
            elif "read" in action_name or "gmail_read" in action_name or "read" in tool_name:
                output = read_gmail_inbox(
                    folder=params.get("folder", "inbox"),
                    status_filter=params.get("status_filter", "ALL"),
                    sender_email=params.get("sender_email", ""),
                    days_ago=params.get("days_ago", ""),
                    limit=params.get("limit", 10)
                )
                return {"success": True, "output": output}
            elif "search" in action_name or "gmail_search" in action_name or "search" in tool_name:
                output = search_gmail_inbox(
                    from_email=params.get("from_email") or params.get("from"),
                    to_email=params.get("to_email") or params.get("to"),
                    subject=params.get("subject"),
                    content=params.get("content") or params.get("query"),
                    has_attachment=params.get("has_attachment", False),
                    attachment_name=params.get("attachment_name"),
                    label=params.get("label"),
                    category=params.get("category"),
                    after_date=params.get("after_date"),
                    before_date=params.get("before_date"),
                    include_spam_trash=params.get("include_spam_trash", False),
                    limit=params.get("max_results", 10) or params.get("limit", 10)
                )
                return {"success": True, "output": output}
            elif "mark" in action_name or "gmail_mark_read" in action_name:
                output = mark_gmail_read(
                    message_id=params.get("message_id"),
                    folder=params.get("folder", "inbox")
                )
                return {"success": True, "output": output}
                
        # Jira
        elif "jira" in tool_name:
            from tools.jira_tools import create_issue, get_issues, add_comment
            if "create" in action_name:
                output = create_issue(
                    project_key=params.get("projectKey") or params.get("project_key"),
                    summary=params.get("summary"),
                    description=params.get("description", ""),
                    issue_type=params.get("issue_type") or params.get("issueType") or "Task"
                )
                return {"success": True, "output": output}
            elif "get" in action_name:
                output = get_issues(
                    project_key=params.get("projectKey") or params.get("project_key"),
                    limit=params.get("limit", 5)
                )
                return {"success": True, "output": output}
            elif "comment" in action_name:
                output = add_comment(
                    issue_key=params.get("issueKey") or params.get("issue_key"),
                    comment=params.get("comment")
                )
                return {"success": True, "output": output}
                
        # ServiceNow
        elif "servicenow" in tool_name:
            from tools.servicenow_tools import create_incident, get_incidents, update_incident, query_table
            if "create" in tool_name or "create" in action_name:
                output = create_incident(
                    short_description=params.get("short_description") or params.get("shortDescription"),
                    description=params.get("description") or params.get("short_description") or "",
                    urgency=params.get("urgency", "3"),
                    severity=params.get("severity", "3")
                )
                return {"success": True, "output": output}
            elif "get" in tool_name or "get" in action_name:
                output = get_incidents(
                    limit=params.get("limit", 5),
                    state=params.get("state")
                )
                return {"success": True, "output": output}
            elif "update" in tool_name or "update" in action_name:
                output = update_incident(
                    sys_id=params.get("sys_id") or params.get("sysId"),
                    state=params.get("state"),
                    comments=params.get("comments")
                )
                return {"success": True, "output": output}
            elif "query" in tool_name or "query" in action_name:
                output = query_table(
                    table_name=params.get("table_name", "incident"),
                    query=params.get("query"),
                    limit=params.get("limit", 5)
                )
                return {"success": True, "output": output}

        # Salesforce
        elif "salesforce" in tool_name:
            from tools.salesforce_tools import query_salesforce, create_salesforce_record
            if "query" in tool_name or "query" in action_name:
                output = query_salesforce(query=params.get("query"))
                return {"success": True, "output": output}
            elif "create" in tool_name or "create" in action_name:
                output = create_salesforce_record(
                    object_type=params.get("object_type") or params.get("objectType"),
                    data=params.get("data")
                )
                return {"success": True, "output": output}

        # AI Agent
        elif tool_name == "ai_agent":
            from agent import run_agent_for_project
            agent_id = params.get("agent_id")
            query = params.get("query")
            if not agent_id or not query:
                raise Exception("Missing agent_id or query for AI Agent node")
            output = run_agent_for_project(
                user_id=user_id,
                agent_id=int(agent_id),
                thread_id=0,
                prompt=query
            )
            return {"success": True, "output": output}

        # Generic TOOL_REGISTRY fallback
        for reg_id, reg_info in TOOL_REGISTRY.items():
            if reg_id.lower() == tool_name or reg_id.lower() == full_action:
                funcs = reg_info.get("functions", [])
                if funcs:
                    output = funcs[0](**params)
                    return {"success": True, "output": output}
                    
        raise Exception(f"Action '{action_name}' on piece '{tool_name}' is not supported or not implemented in python registry.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    finally:
        if token_conn:
            current_connection_id.reset(token_conn)
        if token_user:
            current_user_id.reset(token_user)




class WorkflowExecuteRequest(BaseModel):
    input_data: dict
    steps: list = []


import sys
import os
v2_backend_dir = os.path.join(os.path.dirname(__file__), "..", "v2", "backend")
if v2_backend_dir not in sys.path:
    sys.path.append(v2_backend_dir)

from schemas import get_node_catalog, get_piece_schema

@app.get("/api/nodes/schema")
async def get_nodes_schema():
    return {"nodes": get_node_catalog()}

@app.get("/api/nodes/schema/{piece_name}")
async def get_node_schema(piece_name: str):
    schema = get_piece_schema(piece_name)
    if not schema:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Piece schema not found")
    return schema

@app.post("/api/workflows/test_node")
async def api_test_node(request: Request, current_user: dict = Depends(get_current_user)):
    data = await request.json()
    piece_name = data.get('piece_name')
    action_name = data.get('action_name', 'send_email')
    
    if piece_name == 'gmail' and action_name == 'default':
        action_name = 'send_email'
        
    config = data.get('config', {})
    
    variables = data.get('variables', [])
    initial_data = {}
    for v in variables:
        initial_data[v.get('name')] = v.get('value')
        
    # We proxy directly to the piece executor at port 3001
    payload = {
        "steps": [
            {
                "id": "test_step",
                "type": f"{piece_name}::{action_name}",
                "data": config
            }
        ],
        "initialData": initial_data
    }
    
    # If piece_name is manual, return simulated success
    if piece_name == 'manual':
        return {"success": True, "output": config}
        
    if piece_name == 'ai' and action_name == 'agent':
        try:
            from workflows import resolve_params
            resolved = resolve_params(config, initial_data)
            agent_id = resolved.get('agent_id')
            query = resolved.get('query')
            
            if not agent_id or not query:
                return {"success": False, "error": "Agent ID and query are required."}
                
            from database import get_agent
            user_id = current_user["user_id"]
            agent = get_agent(user_id, agent_id)
            if not agent:
                return {"success": False, "error": f"Agent {agent_id} not found."}
                
            # Execute the agent
            from agent import run_agent_for_project
            # Create a dummy thread ID of 0 for stateless workflow node executions
            result = run_agent_for_project(user_id=user_id, agent_id=agent_id, thread_id=0, prompt=query)
            
            return {"success": True, "output": result}
        except Exception as e:
            return {"success": False, "error": f"AI Agent error: {str(e)}"}
        
    import httpx
    try:
        headers = {}
        auth_header = request.headers.get("authorization")
        if auth_header:
            headers["Authorization"] = auth_header
            
        async with httpx.AsyncClient() as client:
            res = await client.post("http://127.0.0.1:3001/execute_workflow", json=payload, headers=headers, timeout=30.0)
            if res.status_code == 200:
                data = res.json()
                logs = data.get("logs", [])
                error_msg = None
                for log in logs:
                    if log.get("error"):
                        error_msg = log["error"]
                        break
                
                if error_msg:
                    return {"success": False, "error": error_msg}
                return {"success": data.get("success", False), "output": data.get("context", {}).get("test_step")}
            else:
                return {"success": False, "error": res.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


import uuid
import asyncio

async def background_workflow_execution(workflow_id: str, user_id: int, payload: dict, token: str):
    task_id = payload["task_id"]
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    variables = payload.get("variables", [])
    
    from database import create_workflow_run, update_workflow_run
    try:
        run_id = create_workflow_run(user_id, int(workflow_id), status="running")
    except Exception as db_err:
        print(f"Failed to create run log: {db_err}")
        run_id = None

    
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
        
        # Parse and prepare nodes for the graph engine
        graph_nodes = []
        for n in nodes:
            config = n.get("data", {}).get("config", {})
            piece_name = n.get("data", {}).get("piece", "core")
            action_name = n.get("data", {}).get("action", "")
            
            if "_" in piece_name and not piece_name.startswith("@"):
                parts = piece_name.split("_", 1)
                piece_name = parts[0]
                if not action_name:
                    action_name = parts[1]
                    
            if not action_name:
                label = n.get("data", {}).get("label", "")
                if ": " in label:
                    action_name = label.split(": ")[1].strip().lower().replace(" ", "_")
                elif piece_name == "gmail":
                    action_name = "send_email"
                    
            graph_nodes.append({
                "id": n["id"],
                "type": n.get("type", ""),
                "piece_name": piece_name,
                "action_name": action_name,
                "data": config
            })

            async with httpx.AsyncClient(timeout=None) as client:
              res = await client.post("http://127.0.0.1:3001/execute_workflow", json={
                  "nodes": nodes,
                  "edges": edges,
                  "initialData": initial_data,
                  "task_id": task_id,
                  "workflow_id": workflow_id,
                  "webhookUrl": f"http://127.0.0.1:8000/api/workflows/{workflow_id}/webhook/{task_id}"
              }, headers=headers)
            
            data = res.json()
            logs = data.get("logs", [])
            
            if run_id:
                final_status = "success"
                for log in logs:
                    if not log.get("success", False):
                        final_status = "error"
                        break
                try:
                    update_workflow_run(run_id, final_status, logs)
                except Exception as db_err:
                    print(f"Failed to update run log: {db_err}")
        
        await manager.broadcast({
            "type": "workflow_complete",
            "data": {"workflow_id": workflow_id, "task_id": task_id, "results": data.get("context", {})}
        })
    except Exception as e:
        if 'run_id' in locals() and run_id:
            try:
                update_workflow_run(run_id, "error", [{"step": "system", "error": str(e), "success": False}])
            except Exception:
                pass
        await manager.broadcast({
            "type": "workflow_error",
            "data": {"workflow_id": workflow_id, "task_id": task_id, "error": str(e)}
        })


@app.post("/api/workflows/{workflow_id}/webhook/{task_id}")
async def workflow_webhook(workflow_id: str, task_id: str, request: Request):
    data = await request.json()
    data["workflow_id"] = workflow_id
    data["task_id"] = task_id
    await manager.broadcast({
        "type": data["type"],
        "data": data
    })
    return {"success": True}

@app.post("/api/workflows/{workflow_id}/stop/{task_id}")
async def stop_workflow(workflow_id: str, task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            res = await client.post("http://127.0.0.1:3001/stop_workflow", json={"task_id": task_id, "workflow_id": workflow_id})
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: str, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    data = await request.json()
    is_test = data.get("is_test", False)

    if str(workflow_id) != "new_workflow" and not is_test:
        wf = get_workflow(current_user["user_id"], int(workflow_id))
        if wf and wf.get("status") != "active":
            raise HTTPException(status_code=400, detail="Cannot execute inactive workflow")

    
    # Auto-remove cycles
    edges = data.get("edges", [])
    adj = {}
    for e in edges:
        src, tgt = e.get("source"), e.get("target")
        if src not in adj: adj[src] = []
        adj[src].append(tgt)
        
    visited = set()
    rec_stack = set()
    safe_edges = []
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in adj.get(node, []):
            is_back_edge = neighbor in rec_stack
            if not is_back_edge:
                # Find the edge object and keep it
                for e in edges:
                    if e.get("source") == node and e.get("target") == neighbor:
                        if e not in safe_edges:
                            safe_edges.append(e)
                if neighbor not in visited:
                    dfs(neighbor)
        rec_stack.remove(node)
        
    for node in list(adj.keys()):
        if node not in visited:
            dfs(node)
            
    # Update data with safe edges only
    data["edges"] = safe_edges
    
    task_id = str(uuid.uuid4())
    data["task_id"] = task_id
    token = request.headers.get("authorization")
    
    background_tasks.add_task(background_workflow_execution, workflow_id, current_user["user_id"], data, token)
    return {"task_id": task_id, "status": "dispatched"}



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

# --- Health ---

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# --- Projects API ---

@app.get("/api/projects")
async def api_get_projects(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    from database import get_conn, _execute, _fetchall_as_dicts, USE_POSTGRES
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    else:
        cur = _execute(conn, 'SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    projects = _fetchall_as_dicts(cur)
    conn.close()
    return {"projects": projects}

@app.post("/api/projects")
async def api_create_project(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
        
    data = await request.json()
    name = data.get("name")
    description = data.get("description", "")
    
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
        
    from database import get_conn, _execute, USE_POSTGRES
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'INSERT INTO projects (user_id, name, description) VALUES (%s, %s, %s) RETURNING id', (user_id, name, description))
        project_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)', (user_id, name, description))
        project_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": project_id, "name": name, "description": description}

@app.get("/api/projects/{project_id}")
async def api_get_project(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
        
    from database import get_conn, _execute, _fetchone_as_dict, USE_POSTGRES
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM projects WHERE id = %s AND user_id = %s', (project_id, user_id))
    else:
        cur = _execute(conn, 'SELECT * FROM projects WHERE id = ? AND user_id = ?', (project_id, user_id))
    project = _fetchone_as_dict(cur)
    conn.close()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {"project": project}

@app.delete("/api/projects/{project_id}")
async def api_delete_project(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    from database import get_conn, _execute, USE_POSTGRES
    
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'DELETE FROM projects WHERE id = %s AND user_id = %s', (project_id, user_id))
    else:
        # SQLite doesn't always have ON DELETE CASCADE enabled by default, manual cascading
        _execute(conn, 'DELETE FROM chat_history WHERE thread_id IN (SELECT id FROM chat_threads WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM chat_threads WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM vector_documents WHERE doc_id IN (SELECT id FROM knowledge_base WHERE agent_id IN (SELECT id FROM agents WHERE project_id = ? AND user_id = ?))', (project_id, user_id))
        _execute(conn, 'DELETE FROM knowledge_base WHERE agent_id IN (SELECT id FROM agents WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM agents WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM workflow_runs WHERE workflow_id IN (SELECT id FROM workflows WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM workflows WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM projects WHERE id = ? AND user_id = ?', (project_id, user_id))
        
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Project deleted"}



@app.get("/api/projects/{project_id}/agents")
async def api_get_project_agents(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
        
    from database import get_conn, _execute, _fetchall_as_dicts, USE_POSTGRES
    import json
    
    conn = get_conn()
    # Also verify project belongs to user
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM agents WHERE project_id = %s AND user_id = %s ORDER BY id DESC', (project_id, user_id))
    else:
        cur = _execute(conn, 'SELECT * FROM agents WHERE project_id = ? AND user_id = ? ORDER BY id DESC', (project_id, user_id))
    agents = _fetchall_as_dicts(cur)
    conn.close()
    
    for row in agents:
        try:
            row["connected_tools"] = json.loads(row.get("connected_tools") or "[]")
        except:
            row["connected_tools"] = []
            
    return {"agents": agents}

# --- Page Routes ---

@app.get("/project/{project_id}")
async def serve_project_workspace(project_id: int):
    response = FileResponse(os.path.join(static_dir, "project.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/login")
async def serve_login_page():
    return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/signup")
async def serve_signup_page():
    return FileResponse(os.path.join(static_dir, "signup.html"))

@app.get("/api/pieces")
async def get_pieces():
    import httpx
    
    mock_pieces = [
        {"name": "slack", "displayName": "Slack", "description": "Send messages to Slack"},
        {"name": "gmail", "displayName": "Gmail", "description": "Send and read emails"},
        {"name": "hubspot", "displayName": "HubSpot", "description": "Manage CRM contacts"},
        {"name": "openai", "displayName": "OpenAI", "description": "Generate text and AI responses"}
    ]
    
    try:
        # Fast timeout so it doesn't hang the UI
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get("http://127.0.0.1:3001/pieces")
            if res.status_code == 200:
                json_data = res.json()
                if isinstance(json_data, list):
                    data = json_data
                else:
                    data = json_data.get("data", [])
                
                if len(data) > 0:
                    return {"pieces": data}
    except Exception as e:
        print("Lightweight engine pieces unavailable, falling back to mock pieces", e)
        pass
        
    # Fallback to mock pieces if Lightweight engine is down or times out
    return {"pieces": mock_pieces}



# Serve V2 React Canvas
v2_frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v2", "frontend", "dist"))
if os.path.exists(v2_frontend_dist):
    # Mount assets folder for React build
    assets_dir = os.path.join(v2_frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="v2_assets")
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        import sys
        print(f"Validation Error: {exc.errors()} for body {await request.body()}", file=sys.stderr)
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.get("/v2-canvas")
    @app.get("/v2-dashboard")
    async def serve_v2_canvas():
        response = FileResponse(os.path.join(v2_frontend_dist, "index.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# Serve static files and index
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


