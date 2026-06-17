import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if '/api/pieces' not in content:
    pieces_endpoint = '''
@app.get("/api/pieces")
async def get_pieces():
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get("http://localhost:3000/api/v1/pieces")
            if res.status_code == 200:
                # Format to match what frontend expects: { pieces: [...] }
                return {"pieces": res.json().get("data", [])}
            return {"pieces": []}
    except Exception as e:
        return {"pieces": [], "error": str(e)}
'''
    content += pieces_endpoint
    with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
