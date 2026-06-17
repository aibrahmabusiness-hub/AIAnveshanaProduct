import sys
import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoint_code = """
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

    system_msg = \"\"\"You are an expert AI agent architect. 
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
  "system_prompt": "Role: ...\\nGoal: ...\\nActions: ...\\nResult: ..."
}
\"\"\"

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
"""

if "@app.post(\"/api/agents/generate_from_prompt\")" not in text:
    # Insert after /api/agents
    target = '@app.get("/api/agents")'
    if target in text:
        text = text.replace(target, endpoint_code + '\n' + target)
    
with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("main.py patched for agent generation.")
