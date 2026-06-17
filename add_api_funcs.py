import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports to main.py
if 'get_all_credentials' not in content:
    content = content.replace('save_credentials, get_credentials, create_user', 'save_credentials, get_credentials, get_all_credentials, delete_credentials, create_user')

new_code = '''
class CredentialRequest(BaseModel):
    tool_name: str
    credentials: dict

@app.get("/api/credentials")
async def api_get_credentials(current_user: dict = Depends(get_current_user)):
    try:
        creds = get_all_credentials(current_user["id"])
        return {"success": True, "credentials": creds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credentials")
async def api_save_credentials(req: CredentialRequest, current_user: dict = Depends(get_current_user)):
    try:
        save_credentials(current_user["id"], req.tool_name, req.credentials)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/credentials/{tool_name}")
async def api_delete_credentials(tool_name: str, current_user: dict = Depends(get_current_user)):
    try:
        delete_credentials(current_user["id"], tool_name)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

if '/api/credentials' not in content:
    content = content.replace('# --- Health ---', new_code + '\n# --- Health ---')

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
