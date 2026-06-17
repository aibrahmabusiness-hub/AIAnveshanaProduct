import re

filepath = r'c:\Users\Admin\Documents\Agentic AI\backend\main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """      # We proxy directly to the piece executor at port 3001
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
                  return {"success": False, "error": res.text}"""

new_code = """      # We proxy directly to the piece executor at port 3001
      payload = {
          "steps": [
              {
                  "id": "test_step",
                  "type": f"{piece_name}::{action_name}",
                  "config": config
              }
          ]
      }
      
      # If piece_name is manual, return simulated success
      if piece_name == 'manual':
          return {"success": True, "output": config}
          
      import httpx
      try:
          async with httpx.AsyncClient() as client:
              res = await client.post("http://127.0.0.1:3001/execute_workflow", json=payload, timeout=30.0)
              if res.status_code == 200:
                  data = res.json()
                  return {"success": data.get("success", False), "output": data.get("context", {}).get("test_step")}
              else:
                  return {"success": False, "error": res.text}"""

content = content.replace(old_code, new_code)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
