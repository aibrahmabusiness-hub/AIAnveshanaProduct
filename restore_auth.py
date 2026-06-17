import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

auth_endpoints = '''
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
    
    orgs = get_user_organizations(user["id"])
    if not orgs:
        raise HTTPException(status_code=403, detail="User does not belong to any organization")
        
    default_org = orgs[0]
    token = create_access_token({
        "user_id": user["id"], 
        "username": user["username"], 
        "role": default_org["role"],
        "organization_id": default_org["id"]
    })
    
    return {
        "status": "success", 
        "access_token": token, 
        "token_type": "bearer",
        "username": user["username"],
        "organization": default_org["name"]
    }
'''

if '@app.post("/api/auth/login")' not in content:
    content = content.replace('class WorkflowExecuteRequest(BaseModel):', auth_endpoints + '\nclass WorkflowExecuteRequest(BaseModel):')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
