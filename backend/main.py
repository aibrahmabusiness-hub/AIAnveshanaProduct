import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List

from agent import run_agent_for_project
from database import (
    init_db, create_agent, get_all_agents, get_agent, update_agent_tools,
    add_knowledge, get_knowledge, delete_knowledge, get_chat_history,
    save_credentials, get_credentials, create_user, get_user_by_username,
    add_llm_config, get_all_llm_configs, set_default_llm_config, delete_llm_config, update_agent_llm,
    create_workflow, get_workflows, get_workflow, delete_workflow,
    create_chat_thread, get_chat_threads, get_chat_thread, delete_chat_thread,
    update_agent, add_chat_message, delete_agent
)
from auth import hash_password, verify_password, create_access_token, get_current_user
from vector_store import add_to_vector_store, delete_from_vector_store
from workflows import execute_workflow
from tools.tool_registry import get_available_tools

app = FastAPI(title="AI Anveshana Platform")

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
    agent_id: int
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

class LLMTestRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str

class CredentialTestRequest(BaseModel):
    tool_name: str
    credentials: dict

class AgentLLMRequest(BaseModel):
    llm_config_id: Optional[int] = None

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
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# --- Agent Endpoints ---

@app.get("/api/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return {"agents": get_all_agents(user_id)}

@app.post("/api/agents")
async def create_new_agent(request: AgentRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    new_agent = create_agent(user_id, request.name, request.description, request.system_prompt, request.connected_tools)
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
        thread = create_chat_thread(user_id, request.agent_id, request.title)
        return thread
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")

@app.get("/api/chat/threads")
async def list_threads(agent_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    threads = get_chat_threads(user_id, agent_id)
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

@app.post("/api/knowledge/{agent_id}")
async def upload_knowledge(agent_id: int, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    
    # Save to database
    doc = add_knowledge(user_id, agent_id, file.filename, text_content)
    
    # Add to ChromaDB vector store
    try:
        add_to_vector_store(agent_id, doc["id"], file.filename, text_content)
    except Exception as e:
        print(f"[Main] Vector store insert warning: {e}")
        
    return doc

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

@app.post("/api/credentials")
async def save_tool_credentials(request: CredentialRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    existing = get_credentials(user_id, request.tool_name) or {}
    new_creds = dict(request.credentials)
    for k, v in new_creds.items():
        if v == "********" and k in existing:
            new_creds[k] = existing[k]
    save_credentials(user_id, request.tool_name, new_creds)
    return {"status": "saved"}

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
            return {"status": "success", "message": "Successfully connected to ServiceNow."}
            
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
            return {"status": "success", "message": "Successfully connected to Salesforce."}
            
        elif tool_name == "gmail":
            username = creds.get("username")
            password = creds.get("password")
            
            if not username or not password:
                raise Exception("Missing Gmail email or App Password.")
                
            import smtplib
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=8)
            server.login(username, password)
            server.quit()
            return {"status": "success", "message": "Successfully connected to Gmail SMTP."}
            
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
            return {"status": "success", "message": f"Successfully connected to Jira. User: {res.json().get('displayName', email)}"}
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool_name}")
            
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

@app.get("/api/credentials/{tool_name}")
async def get_tool_credentials_status(tool_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    creds = get_credentials(user_id, tool_name)
    is_configured = bool(creds) and (creds.get("configured") is True or bool(creds.get("username")) or bool(creds.get("instance_url")))
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
    config = add_llm_config(user_id, request.provider, request.model_name, request.api_key)
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
            res = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Mistral API returned status {res.status_code}: {res.text}")
            text = res.json()["choices"][0]["message"]["content"]
            return {"status": "success", "message": f"Successfully connected. Response: {text.strip()}"}
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

@app.get("/api/settings/llm")
async def list_llm_configs(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    configs = get_all_llm_configs(user_id)
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

@app.post("/api/workflows")
async def create_new_workflow(request: WorkflowRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        workflow = create_workflow(user_id, request.agent_id, request.name, request.steps)
        return workflow
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")

@app.get("/api/workflows")
async def list_workflows(agent_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    workflows = get_workflows(user_id, agent_id)
    return {"workflows": workflows}

@app.get("/api/workflows/{workflow_id}")
async def get_single_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    workflow = get_workflow(user_id, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.delete("/api/workflows/{workflow_id}")
async def remove_workflow(workflow_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    delete_workflow(user_id, workflow_id)
    return {"status": "deleted"}

@app.post("/api/workflows/{workflow_id}/execute")
async def run_workflow(workflow_id: int, request: WorkflowExecuteRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    res = execute_workflow(user_id, workflow_id, request.input_data)
    return res

# --- Health ---

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# --- Page Routes ---

@app.get("/project/{project_id}")
async def serve_project_workspace(project_id: int):
    return FileResponse(os.path.join(static_dir, "project.html"))

@app.get("/login")
async def serve_login_page():
    return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/signup")
async def serve_signup_page():
    return FileResponse(os.path.join(static_dir, "signup.html"))

# Serve static files and index
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

