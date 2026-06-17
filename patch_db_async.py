import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\database.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update init_db to add sync_status
if "ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS sync_status" not in content:
    init_db_patch = """        cursor.execute("ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS sync_status TEXT DEFAULT 'processing'")"""
    content = content.replace(
        """        cursor.execute("ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")""",
        init_db_patch
    )

# 2. Update add_knowledge to return processing by default
old_add = """def add_knowledge(user_id, agent_id, filename, content):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content) VALUES (%s, %s, %s) RETURNING id', (agent_id, filename, content))
        kb_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content) VALUES (?, ?, ?)', (agent_id, filename, content))
        kb_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": kb_id, "agent_id": agent_id, "filename": filename}"""

new_add = """def add_knowledge(user_id, agent_id, filename, content):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content, sync_status) VALUES (%s, %s, %s, %s) RETURNING id', (agent_id, filename, content, 'processing'))
        kb_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content, sync_status) VALUES (?, ?, ?, ?)', (agent_id, filename, content, 'processing'))
        kb_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": kb_id, "agent_id": agent_id, "filename": filename, "sync_status": "processing"}"""

content = content.replace(old_add, new_add)

# 3. Update get_knowledge
old_get = """def get_knowledge(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        return []
    conn = get_conn()
    cur = _execute(conn, 'SELECT id, filename, uploaded_at FROM knowledge_base WHERE agent_id = ?', (agent_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    return rows"""

new_get = """def get_knowledge(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        return []
    conn = get_conn()
    cur = _execute(conn, 'SELECT id, filename, uploaded_at, sync_status FROM knowledge_base WHERE agent_id = %s' if USE_POSTGRES else 'SELECT id, filename, uploaded_at, sync_status FROM knowledge_base WHERE agent_id = ?', (agent_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    return rows"""

content = content.replace(old_get, new_get)

# 4. Add update_knowledge_status and get_knowledge_content_by_id
helpers = """
def update_knowledge_status(kb_id: int, status: str):
    conn = get_conn()
    _execute(conn, 'UPDATE knowledge_base SET sync_status = %s WHERE id = %s' if USE_POSTGRES else 'UPDATE knowledge_base SET sync_status = ? WHERE id = ?', (status, kb_id))
    conn.commit()
    conn.close()

def get_knowledge_content_by_id(user_id, kb_id):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT kb.content, kb.filename, kb.agent_id, a.user_id FROM knowledge_base kb JOIN agents a ON kb.agent_id = a.id WHERE kb.id = %s', (kb_id,))
    else:
        cur = _execute(conn, 'SELECT kb.content, kb.filename, kb.agent_id, a.user_id FROM knowledge_base kb JOIN agents a ON kb.agent_id = a.id WHERE kb.id = ?', (kb_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row or row[3] != user_id:
        raise PermissionError("User does not own this document")
    
    return {"content": row[0], "filename": row[1], "agent_id": row[2]}

"""

if "def update_knowledge_status" not in content:
    content += helpers

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched database.py successfully.")
