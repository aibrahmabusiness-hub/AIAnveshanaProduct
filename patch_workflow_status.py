import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\database.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_func = """def update_workflow_status(user_id, workflow_id, status):
    conn = get_conn()
    
    # Verify ownership
    cur = _execute(conn, 'SELECT id FROM workflows WHERE id = ? AND user_id = ?', (workflow_id, user_id))
    if not cur.fetchone():
        conn.close()
        raise PermissionError("User does not own this workflow")
        
    if USE_POSTGRES:
        _execute(conn, 'UPDATE workflows SET status = %s WHERE id = %s', (status, workflow_id))
    else:
        _execute(conn, 'UPDATE workflows SET status = ? WHERE id = ?', (status, workflow_id))
    conn.commit()
    conn.close()"""

new_func = """def update_workflow_status(user_id, workflow_id, status):
    conn = get_conn()
    
    # Verify ownership
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT id FROM workflows WHERE id = %s AND user_id = %s', (workflow_id, user_id))
    else:
        cur = _execute(conn, 'SELECT id FROM workflows WHERE id = ? AND user_id = ?', (workflow_id, user_id))
        
    if not cur.fetchone():
        conn.close()
        raise PermissionError("User does not own this workflow")
        
    if USE_POSTGRES:
        _execute(conn, 'UPDATE workflows SET status = %s WHERE id = %s', (status, workflow_id))
    else:
        _execute(conn, 'UPDATE workflows SET status = ? WHERE id = ?', (status, workflow_id))
    conn.commit()
    conn.close()"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed update_workflow_status in database.py")
else:
    print("Could not find exact function signature")
