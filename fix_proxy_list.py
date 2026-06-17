import re

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

correct_logic = '''        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get("http://127.0.0.1:3000/api/v1/pieces")
            if res.status_code == 200:
                json_data = res.json()
                if isinstance(json_data, list):
                    data = json_data
                else:
                    data = json_data.get("data", [])
                
                if len(data) > 0:
                    return {"pieces": data}'''

content = re.sub(r'async with httpx\.AsyncClient\(timeout=2\.0\) as client:.*?return \{"pieces": data\}', correct_logic, content, flags=re.DOTALL)

with open('C:/Users/Admin/Documents/Agentic AI/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
