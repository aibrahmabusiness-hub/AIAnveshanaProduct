"""
Database layer — Cloud PostgreSQL (Supabase) with SQLite fallback.
If DATABASE_URL is set → uses PostgreSQL (production/cloud)
If not → falls back to local SQLite (development)
"""
import os
import json
import contextvars
from dotenv import load_dotenv
from encryption import encrypt_key, decrypt_key, mask_key

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

current_user_id = contextvars.ContextVar("current_user_id", default=None)

# --- Connection Helpers ---

def get_conn():
    if USE_POSTGRES:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "anveshana.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def _execute(conn, query, params=None):
    """Execute a query, adapting placeholder syntax for PG vs SQLite."""
    if USE_POSTGRES and '?' in query:
        query = _convert_placeholders(query)
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor

def _convert_placeholders(query: str) -> str:
    """Convert SQLite ? placeholders to PostgreSQL %s."""
    return query.replace('?', '%s')

def _fetchall_as_dicts(cursor) -> list:
    """Convert cursor results to list of dicts (works for both PG and SQLite)."""
    if USE_POSTGRES:
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        return [dict(row) for row in cursor.fetchall()]

def _fetchone_as_dict(cursor):
    """Convert single cursor result to dict."""
    if USE_POSTGRES:
        if cursor.description is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(zip(columns, row))
    else:
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

# --- Schema Init ---

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    from auth import hash_password

    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT DEFAULT '',
                user_prompt TEXT DEFAULT '',
                creativity REAL DEFAULT 0.5,
                guardrails BOOLEAN DEFAULT TRUE,
                max_tool_calls INTEGER DEFAULT 80,
                connected_tools TEXT DEFAULT '[]',
                llm_config_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_threads (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                thread_id INTEGER NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_credentials (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                tool_name TEXT NOT NULL,
                credentials TEXT NOT NULL DEFAULT '{}',
                CONSTRAINT unique_user_tool UNIQUE (user_id, tool_name)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_config (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                provider TEXT NOT NULL,
                model_name TEXT NOT NULL,
                api_key_encrypted TEXT NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                steps TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')

        # Run Alter statements to add user_id column if tables were created previously
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE llm_config ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE tool_credentials ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("SELECT 1 FROM pg_constraint WHERE conname = 'unique_user_tool'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE tool_credentials ADD CONSTRAINT unique_user_tool UNIQUE (user_id, tool_name)")
            except Exception:
                pass
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS user_prompt TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS creativity REAL DEFAULT 0.5")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS guardrails BOOLEAN DEFAULT TRUE")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS max_tool_calls INTEGER DEFAULT 80")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS guardrail_types TEXT DEFAULT '[]'")
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT DEFAULT '',
                user_prompt TEXT DEFAULT '',
                creativity REAL DEFAULT 0.5,
                guardrails BOOLEAN DEFAULT 1,
                max_tool_calls INTEGER DEFAULT 80,
                connected_tools TEXT DEFAULT '[]',
                llm_config_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                agent_id INTEGER,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tool_name TEXT NOT NULL,
                credentials TEXT NOT NULL DEFAULT '{}',
                UNIQUE(user_id, tool_name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                provider TEXT NOT NULL,
                model_name TEXT NOT NULL,
                api_key_encrypted TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                agent_id INTEGER,
                name TEXT NOT NULL,
                steps TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        ''')

        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN user_id INTEGER")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE llm_config ADD COLUMN user_id INTEGER")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN user_prompt TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN creativity REAL DEFAULT 0.5")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN guardrails BOOLEAN DEFAULT 1")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN max_tool_calls INTEGER DEFAULT 80")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN guardrail_types TEXT DEFAULT '[]'")
        except Exception:
            pass

    conn.commit()

    # Create default superadmin
    try:
        if USE_POSTGRES:
            cursor.execute("SELECT id FROM users WHERE username = %s", ("admin",))
        else:
            cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        admin_row = cursor.fetchone()
        if not admin_row:
            pwd_hash = hash_password("Anveshana@2026")
            if USE_POSTGRES:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ("admin", pwd_hash, "superadmin")
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", pwd_hash, "superadmin")
                )
            conn.commit()
            print("[DB] Created default superadmin 'admin' / 'Anveshana@2026'")
    except Exception as e:
        print(f"[DB] Error creating default superadmin: {e}")

    conn.close()
    db_type = "PostgreSQL (Supabase)" if USE_POSTGRES else "SQLite (local)"
    print(f"[DB] Initialized: {db_type}")

# --- User CRUD ---

def create_user(username, email, password_hash, role="user"):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn,
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, email, password_hash, role))
        user_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, role))
        user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": user_id, "username": username, "email": email, "role": role}

def get_user_by_username(username):
    conn = get_conn()
    cur = _execute(conn, "SELECT * FROM users WHERE username = ?", (username,))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

def get_user(user_id):
    conn = get_conn()
    cur = _execute(conn, "SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

# --- Agent CRUD ---

def create_agent(user_id, name, description, system_prompt="", user_prompt="", creativity=0.5, guardrails=True, max_tool_calls=80, connected_tools=None, llm_config_id=None, guardrail_types=None):
    if connected_tools is None:
        connected_tools = []
    if guardrail_types is None:
        guardrail_types = []
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 
            'INSERT INTO agents (user_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, connected_tools, llm_config_id, guardrail_types) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (user_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, json.dumps(connected_tools), llm_config_id, json.dumps(guardrail_types)))
        agent_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO agents (user_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, connected_tools, llm_config_id, guardrail_types) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, json.dumps(connected_tools), llm_config_id, json.dumps(guardrail_types)))
        agent_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": agent_id, "name": name, "description": description, 
        "system_prompt": system_prompt, "user_prompt": user_prompt,
        "creativity": creativity, "guardrails": guardrails, "max_tool_calls": max_tool_calls,
        "connected_tools": connected_tools, "llm_config_id": llm_config_id, "guardrail_types": guardrail_types
    }

def get_all_agents(user_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT * FROM agents WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    for row in rows:
        row["connected_tools"] = json.loads(row.get("connected_tools") or "[]")
        row["guardrail_types"] = json.loads(row.get("guardrail_types") or "[]")
        # Ensure boolean typing compatibility
        row["guardrails"] = bool(row.get("guardrails"))
    return rows

def get_agent(user_id, agent_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT * FROM agents WHERE user_id = ? AND id = ?', (user_id, agent_id))
    row = _fetchone_as_dict(cur)
    conn.close()
    if row:
        row["connected_tools"] = json.loads(row.get("connected_tools") or "[]")
        row["guardrail_types"] = json.loads(row.get("guardrail_types") or "[]")
        row["guardrails"] = bool(row.get("guardrails"))
    return row

def update_agent(user_id, agent_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, llm_config_id=None, guardrail_types=None):
    if guardrail_types is None:
        guardrail_types = []
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn,
            'UPDATE agents SET name=%s, description=%s, system_prompt=%s, user_prompt=%s, creativity=%s, guardrails=%s, max_tool_calls=%s, llm_config_id=%s, guardrail_types=%s WHERE user_id=%s AND id=%s',
            (name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, llm_config_id, json.dumps(guardrail_types), user_id, agent_id))
    else:
        _execute(conn,
            'UPDATE agents SET name=?, description=?, system_prompt=?, user_prompt=?, creativity=?, guardrails=?, max_tool_calls=?, llm_config_id=?, guardrail_types=? WHERE user_id=? AND id=?',
            (name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, llm_config_id, json.dumps(guardrail_types), user_id, agent_id))
    conn.commit()
    conn.close()

def update_agent_tools(user_id, agent_id, connected_tools):
    conn = get_conn()
    _execute(conn, 'UPDATE agents SET connected_tools = ? WHERE user_id = ? AND id = ?', (json.dumps(connected_tools), user_id, agent_id))
    conn.commit()
    conn.close()

def update_agent_llm(user_id, agent_id, llm_config_id):
    conn = get_conn()
    _execute(conn, 'UPDATE agents SET llm_config_id = ? WHERE user_id = ? AND id = ?', (llm_config_id, user_id, agent_id))
    conn.commit()
    conn.close()

def delete_agent(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    _execute(conn, 'DELETE FROM agents WHERE user_id = ? AND id = ?', (user_id, agent_id))
    conn.commit()
    conn.close()

# --- Knowledge Base CRUD ---

def verify_agent_ownership(user_id, agent_id) -> bool:
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT user_id FROM agents WHERE id = %s', (agent_id,))
    else:
        cur = _execute(conn, 'SELECT user_id FROM agents WHERE id = ?', (agent_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    db_user_id = row[0]
    if db_user_id is None:
        if USE_POSTGRES:
            _execute(conn, 'UPDATE agents SET user_id = %s WHERE id = %s', (user_id, agent_id))
        else:
            _execute(conn, 'UPDATE agents SET user_id = ? WHERE id = ?', (user_id, agent_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return db_user_id == user_id

def add_knowledge(user_id, agent_id, filename, content):
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
    return {"id": kb_id, "agent_id": agent_id, "filename": filename}

def get_knowledge(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        return []
    conn = get_conn()
    cur = _execute(conn, 'SELECT id, filename, uploaded_at FROM knowledge_base WHERE agent_id = ?', (agent_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    return rows

def get_knowledge_content(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        return ""
    conn = get_conn()
    cur = _execute(conn, 'SELECT filename, content FROM knowledge_base WHERE agent_id = ?', (agent_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    if not rows:
        return ""
    return "\n\n".join([f"--- Document: {r['filename']} ---\n{r['content']}" for r in rows])

def delete_knowledge(user_id, kb_id):
    conn = get_conn()
    # verify ownership of kb via its agent
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT a.user_id FROM knowledge_base kb JOIN agents a ON kb.agent_id = a.id WHERE kb.id = %s', (kb_id,))
    else:
        cur = _execute(conn, 'SELECT a.user_id FROM knowledge_base kb JOIN agents a ON kb.agent_id = a.id WHERE kb.id = ?', (kb_id,))
    row = cur.fetchone()
    if not row or row[0] != user_id:
        conn.close()
        raise PermissionError("User does not own this document")
    
    _execute(conn, 'DELETE FROM knowledge_base WHERE id = ?', (kb_id,))
    conn.commit()
    conn.close()

# --- Chat Threads & History ---

def verify_thread_ownership(user_id, thread_id) -> bool:
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT user_id FROM chat_threads WHERE id = %s', (thread_id,))
    else:
        cur = _execute(conn, 'SELECT user_id FROM chat_threads WHERE id = ?', (thread_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    db_user_id = row[0]
    if db_user_id is None:
        if USE_POSTGRES:
            _execute(conn, 'UPDATE chat_threads SET user_id = %s WHERE id = %s', (user_id, thread_id))
        else:
            _execute(conn, 'UPDATE chat_threads SET user_id = ? WHERE id = ?', (user_id, thread_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return db_user_id == user_id

def create_chat_thread(user_id, agent_id, title):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'INSERT INTO chat_threads (user_id, agent_id, title) VALUES (%s, %s, %s) RETURNING id', (user_id, agent_id, title))
        thread_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO chat_threads (user_id, agent_id, title) VALUES (?, ?, ?)', (user_id, agent_id, title))
        thread_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": thread_id, "user_id": user_id, "agent_id": agent_id, "title": title}

def get_chat_threads(user_id, agent_id):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = %s AND agent_id = %s ORDER BY id DESC', (user_id, agent_id))
    else:
        cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = ? AND agent_id = ? ORDER BY id DESC', (user_id, agent_id))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    return rows

def get_chat_thread(user_id, thread_id):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = %s AND id = %s', (user_id, thread_id))
    else:
        cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = ? AND id = ?', (user_id, thread_id))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

def delete_chat_thread(user_id, thread_id):
    if not verify_thread_ownership(user_id, thread_id):
        raise PermissionError("Access denied")
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'DELETE FROM chat_threads WHERE id = %s', (thread_id,))
    else:
        _execute(conn, 'DELETE FROM chat_threads WHERE id = ?', (thread_id,))
    conn.commit()
    conn.close()

def add_chat_message(user_id, thread_id, role, message):
    if not verify_thread_ownership(user_id, thread_id):
        raise PermissionError("Access denied")
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'INSERT INTO chat_history (thread_id, role, message) VALUES (%s, %s, %s)', (thread_id, role, message))
    else:
        _execute(conn, 'INSERT INTO chat_history (thread_id, role, message) VALUES (?, ?, ?)', (thread_id, role, message))
    conn.commit()
    conn.close()

def get_chat_history(user_id, thread_id, limit=50):
    if not verify_thread_ownership(user_id, thread_id):
        return []
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT role, message, created_at FROM chat_history WHERE thread_id = %s ORDER BY id DESC LIMIT %s', (thread_id, limit))
    else:
        cur = _execute(conn, 'SELECT role, message, created_at FROM chat_history WHERE thread_id = ? ORDER BY id DESC LIMIT ?', (thread_id, limit))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    return list(reversed(rows))

# --- Tool Credentials ---

def save_credentials(user_id, tool_name, credentials):
    if user_id is None:
        user_id = current_user_id.get()
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn,
            'INSERT INTO tool_credentials (user_id, tool_name, credentials) VALUES (%s, %s, %s) ON CONFLICT (user_id, tool_name) DO UPDATE SET credentials = %s',
            (user_id, tool_name, json.dumps(credentials), json.dumps(credentials)))
    else:
        _execute(conn,
            'INSERT INTO tool_credentials (user_id, tool_name, credentials) VALUES (?, ?, ?) ON CONFLICT(user_id, tool_name) DO UPDATE SET credentials = ?',
            (user_id, tool_name, json.dumps(credentials), json.dumps(credentials)))
    conn.commit()
    conn.close()

def get_credentials(user_id, tool_name):
    if user_id is None:
        user_id = current_user_id.get()
    print(f"[DB Debug] get_credentials for {tool_name}: user_id={user_id}, ContextVar={current_user_id.get()}")
    conn = get_conn()
    cur = _execute(conn, 'SELECT credentials FROM tool_credentials WHERE user_id = ? AND tool_name = ?', (user_id, tool_name))
    row = _fetchone_as_dict(cur)
    conn.close()
    if not row:
        return {}
    return json.loads(row["credentials"])

# --- LLM Config CRUD (Encrypted) ---

def add_llm_config(user_id, provider, model_name, api_key):
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
    return {"id": config_id, "provider": provider, "model_name": model_name, "api_key_masked": mask_key(api_key)}

def get_all_llm_configs(user_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT id, provider, model_name, api_key_encrypted, is_default, created_at FROM llm_config WHERE user_id = ? ORDER BY id', (user_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    for row in rows:
        try:
            decrypted = decrypt_key(row["api_key_encrypted"])
            row["api_key_masked"] = mask_key(decrypted)
        except Exception:
            row["api_key_masked"] = "****"
        del row["api_key_encrypted"]
    return rows

def get_llm_config(user_id, config_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT * FROM llm_config WHERE user_id = ? AND id = ?', (user_id, config_id))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

def get_default_llm_config(user_id):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'SELECT * FROM llm_config WHERE user_id = %s AND is_default = TRUE LIMIT 1', (user_id,))
    else:
        cur = _execute(conn, 'SELECT * FROM llm_config WHERE user_id = ? AND is_default = 1 LIMIT 1', (user_id,))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

def set_default_llm_config(user_id, config_id):
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'UPDATE llm_config SET is_default = FALSE WHERE user_id = %s', (user_id,))
        _execute(conn, 'UPDATE llm_config SET is_default = TRUE WHERE user_id = %s AND id = %s', (user_id, config_id))
    else:
        _execute(conn, 'UPDATE llm_config SET is_default = 0 WHERE user_id = ?', (user_id,))
        _execute(conn, 'UPDATE llm_config SET is_default = 1 WHERE user_id = ? AND id = ?', (user_id, config_id))
    conn.commit()
    conn.close()

def delete_llm_config(user_id, config_id):
    conn = get_conn()
    _execute(conn, 'DELETE FROM llm_config WHERE user_id = ? AND id = ?', (user_id, config_id))
    conn.commit()
    conn.close()

# --- Workflows CRUD ---

def create_workflow(user_id, agent_id, name, steps):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    steps_str = json.dumps(steps) if isinstance(steps, (dict, list)) else steps
    if USE_POSTGRES:
        cur = _execute(conn,
            'INSERT INTO workflows (user_id, agent_id, name, steps) VALUES (%s, %s, %s, %s) RETURNING id',
            (user_id, agent_id, name, steps_str))
        wf_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO workflows (user_id, agent_id, name, steps) VALUES (?, ?, ?, ?)',
            (user_id, agent_id, name, steps_str))
        wf_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": wf_id, "user_id": user_id, "agent_id": agent_id, "name": name, "steps": steps}

def get_workflows(user_id, agent_id=None):
    conn = get_conn()
    if agent_id is not None:
        cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? AND agent_id = ? ORDER BY id DESC', (user_id, agent_id))
    else:
        cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    for row in rows:
        try:
            row["steps"] = json.loads(row["steps"])
        except Exception:
            row["steps"] = []
    return rows

def get_workflow(user_id, workflow_id):
    conn = get_conn()
    cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? AND id = ?', (user_id, workflow_id))
    row = _fetchone_as_dict(cur)
    conn.close()
    if row:
        try:
            row["steps"] = json.loads(row["steps"])
        except Exception:
            row["steps"] = []
    return row

def delete_workflow(user_id, workflow_id):
    conn = get_conn()
    _execute(conn, 'DELETE FROM workflows WHERE user_id = ? AND id = ?', (user_id, workflow_id))
    conn.commit()
    conn.close()
