import sys
import re

with open('backend/database.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace add_llm_config
old_add = """def add_llm_config(user_id, provider, model_name, api_key):
    encrypted = encrypt_key(api_key)
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn,
            'INSERT INTO llm_config (user_id, provider, model_name, api_key_encrypted) VALUES (%s, %s, %s, %s) RETURNING id',
            (user_id, provider, model_name, encrypted))
        config_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO llm_config (user_id, provider, model_name, api_key_encrypted) VALUES (?, ?, ?, ?)',
            (user_id, provider, model_name, encrypted))
        config_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": config_id, "provider": provider, "model_name": model_name, "api_key_masked": mask_key(api_key)}"""

new_add = """def add_llm_config(user_id, provider, model_name, api_key, project_id=None):
    encrypted = encrypt_key(api_key)
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn,
            'INSERT INTO llm_config (user_id, project_id, provider, model_name, api_key_encrypted) VALUES (%s, %s, %s, %s, %s) RETURNING id',
            (user_id, project_id, provider, model_name, encrypted))
        config_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO llm_config (user_id, project_id, provider, model_name, api_key_encrypted) VALUES (?, ?, ?, ?, ?)',
            (user_id, project_id, provider, model_name, encrypted))
        config_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": config_id, "project_id": project_id, "provider": provider, "model_name": model_name, "api_key_masked": mask_key(api_key)}"""

if old_add in text:
    text = text.replace(old_add, new_add)
else:
    print("Warning: old_add not found.")

# Replace get_all_llm_configs
old_get = """def get_all_llm_configs(user_id):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = %s ORDER BY id', (user_id,))
    else:
        cur = _execute(conn, 'SELECT id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = ? ORDER BY id', (user_id,))
    rows = _fetchall_as_dicts(cur)
    for row in rows:
        row["api_key_masked"] = mask_key(decrypt_key(row["api_key_encrypted"]))
        del row["api_key_encrypted"]
    conn.close()
    return rows"""

# Try a regex approach in case formatting differs slightly
get_pattern = re.compile(r'def get_all_llm_configs\(user_id\):.*?return rows', re.DOTALL)

new_get = """def get_all_llm_configs(user_id, project_id=None):
    conn = get_conn()
    if project_id is not None:
        if USE_POSTGRES:
            cur = _execute(conn, 'SELECT id, project_id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = %s AND (project_id IS NULL OR project_id = %s) ORDER BY id', (user_id, project_id))
        else:
            cur = _execute(conn, 'SELECT id, project_id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = ? AND (project_id IS NULL OR project_id = ?) ORDER BY id', (user_id, project_id))
    else:
        if USE_POSTGRES:
            cur = _execute(conn, 'SELECT id, project_id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = %s AND project_id IS NULL ORDER BY id', (user_id,))
        else:
            cur = _execute(conn, 'SELECT id, project_id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = ? AND project_id IS NULL ORDER BY id', (user_id,))
            
    rows = _fetchall_as_dicts(cur)
    for row in rows:
        row["api_key_masked"] = mask_key(decrypt_key(row["api_key_encrypted"]))
        del row["api_key_encrypted"]
    conn.close()
    return rows"""

if get_pattern.search(text):
    text = get_pattern.sub(new_get, text)
else:
    print("Warning: get_all_llm_configs not found exactly. Trying simpler replace.")
    # Maybe we didn't include the mask_key loop. Let's just do a simpler search.
    # We can try replacing just the function definition and query execution.

with open('backend/database.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("database.py updated.")
