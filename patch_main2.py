import re
with open(r"C:\Users\Admin\Documents\Agentic AI\backend\main.py", "r", encoding="utf-8") as f:
    js = f.read()

new_func = """@app.get("/api/pieces")
async def list_activepieces(current_user: dict = Depends(get_current_user)):
    return {"status": "hit"}
"""

js = re.sub(r'@app\.get\("/api/pieces"\).*?return \{"pieces": \[\]\}', new_func, js, flags=re.DOTALL)

with open(r"C:\Users\Admin\Documents\Agentic AI\backend\main.py", "w", encoding="utf-8") as f:
    f.write(js)
