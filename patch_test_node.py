import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\backend\main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add test_node endpoint
test_node_endpoint = """@app.get("/api/nodes/schema/{piece_name}")
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
    config = data.get('config', {})
    
    # We proxy directly to the piece executor at port 3001
    payload = {
        "pieceName": piece_name,
        "actionName": action_name,
        "input": config
    }
    
    # If piece_name is manual, return simulated success
    if piece_name == 'manual':
        return {"success": True, "output": config}
        
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("http://localhost:3001/execute", json=payload, timeout=30.0)
            if res.status_code == 200:
                return res.json()
            else:
                return {"success": False, "error": res.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
"""

content = content.replace("""@app.get("/api/nodes/schema/{piece_name}")
async def get_node_schema(piece_name: str):
    schema = get_piece_schema(piece_name)
    if not schema:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Piece schema not found")
    return schema""", test_node_endpoint)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
