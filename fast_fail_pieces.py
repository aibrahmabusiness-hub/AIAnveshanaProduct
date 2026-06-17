import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

mock_pieces_logic = '''@app.get("/api/pieces")
async def get_pieces():
    import httpx
    
    mock_pieces = [
        {"name": "slack", "displayName": "Slack", "description": "Send messages to Slack"},
        {"name": "gmail", "displayName": "Gmail", "description": "Send and read emails"},
        {"name": "hubspot", "displayName": "HubSpot", "description": "Manage CRM contacts"},
        {"name": "openai", "displayName": "OpenAI", "description": "Generate text and AI responses"}
    ]
    
    try:
        # Fast timeout so it doesn't hang the UI for 10 seconds
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get("http://localhost:3000/api/v1/pieces")
            if res.status_code == 200:
                data = res.json().get("data", [])
                if len(data) > 0:
                    return {"pieces": data}
    except Exception as e:
        print("Activepieces unavailable, falling back to mock pieces", e)
        pass
        
    # Fallback to mock pieces if ActivePieces is down or times out
    return {"pieces": mock_pieces}
'''

content = re.sub(r'@app\.get\("/api/pieces"\).*?return \{"pieces": \[\], "error": str\(e\)\}', mock_pieces_logic, content, flags=re.DOTALL)

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
