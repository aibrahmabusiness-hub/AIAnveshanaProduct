import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

delete_endpoint = """
@app.delete("/api/projects/{project_id}")
async def api_delete_project(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    from database import get_conn, _execute, USE_POSTGRES
    
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'DELETE FROM projects WHERE id = %s AND user_id = %s', (project_id, user_id))
    else:
        # SQLite doesn't always have ON DELETE CASCADE enabled by default, manual cascading
        _execute(conn, 'DELETE FROM chat_history WHERE thread_id IN (SELECT id FROM chat_threads WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM chat_threads WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM vector_documents WHERE doc_id IN (SELECT id FROM knowledge_base WHERE agent_id IN (SELECT id FROM agents WHERE project_id = ? AND user_id = ?))', (project_id, user_id))
        _execute(conn, 'DELETE FROM knowledge_base WHERE agent_id IN (SELECT id FROM agents WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM agents WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM workflow_runs WHERE workflow_id IN (SELECT id FROM workflows WHERE project_id = ? AND user_id = ?)', (project_id, user_id))
        _execute(conn, 'DELETE FROM workflows WHERE project_id = ? AND user_id = ?', (project_id, user_id))
        _execute(conn, 'DELETE FROM projects WHERE id = ? AND user_id = ?', (project_id, user_id))
        
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Project deleted"}

"""

# Insert right after api_get_project
target = '    return {"project": project}'
if target in text:
    text = text.replace(target, target + '\n' + delete_endpoint)
    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched main.py successfully")
else:
    print("Target not found")
