import re
with open('C:/Users/Admin/Documents/Agentic AI/backend/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''
def get_all_credentials(user_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT tool_name, credentials FROM tool_credentials WHERE user_id = ?', (user_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    for row in rows:
        try:
            row["credentials"] = json.loads(row["credentials"])
        except:
            row["credentials"] = {}
    return rows

def delete_credentials(user_id, tool_name):
    conn = get_conn()
    _execute(conn, 'DELETE FROM tool_credentials WHERE user_id = ? AND tool_name = ?', (user_id, tool_name))
    conn.commit()
    conn.close()
'''

content = content.replace('def get_credentials(user_id, tool_name):', new_code + '\n\ndef get_credentials(user_id, tool_name):')

with open('C:/Users/Admin/Documents/Agentic AI/backend/database.py', 'w', encoding='utf-8') as f:
    f.write(content)
