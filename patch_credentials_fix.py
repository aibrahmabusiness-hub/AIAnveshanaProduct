import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the first @app.post("/api/credentials") block (Lines 391-399)
old_post_1 = """@app.post("/api/credentials")
async def save_tool_credentials(request: CredentialRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    existing = get_credentials(user_id, request.tool_name) or {}
    new_creds = dict(request.credentials)
    for k, v in new_creds.items():
        if v == "********" and k in existing:
            new_creds[k] = existing[k]
    save_credentials(user_id, request.tool_name, new_creds)
    return {"status": "saved"}"""

if old_post_1 in content:
    content = content.replace(old_post_1, "")

# 2. Fix get_tool_credentials_status to consider any creds as configured
old_get = """@app.get("/api/credentials/{tool_name}")
async def get_tool_credentials_status(tool_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    creds = get_credentials(user_id, tool_name)
    is_configured = bool(creds) and (creds.get("configured") is True or bool(creds.get("username")) or bool(creds.get("instance_url")))
    safe_creds = {}"""

new_get = """@app.get("/api/credentials/{tool_name}")
async def get_tool_credentials_status(tool_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    creds = get_credentials(user_id, tool_name)
    is_configured = bool(creds)
    safe_creds = {}"""

if old_get in content:
    content = content.replace(old_get, new_get)

# 3. Fix the second @app.post("/api/credentials") to save into the connections array!
old_post_2 = """@app.post("/api/credentials")
async def api_save_credentials(req: CredentialRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Verify credentials before saving
        try:
            run_connection_test(req.tool_name, req.credentials)
        except Exception as test_err:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {str(test_err)}")
            
        save_credentials(current_user["user_id"], req.tool_name, req.credentials)
        return {"success": True}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""

new_post_2 = """@app.post("/api/credentials")
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
        raise HTTPException(status_code=500, detail=str(e))"""

if old_post_2 in content:
    content = content.replace(old_post_2, new_post_2)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched main.py successfully")
