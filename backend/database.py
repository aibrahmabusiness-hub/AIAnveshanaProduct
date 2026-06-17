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
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required for cloud deployment (Supabase). SQLite fallback is disabled.")
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(DATABASE_URL)
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
        try:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
        except Exception as e:
            print("Could not enable pgvector:", e)
            
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization_users (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(organization_id, user_id)
            )
        ''')
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
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT DEFAULT '',
                user_prompt TEXT DEFAULT '',
                creativity REAL DEFAULT 0.5,
                guardrails BOOLEAN DEFAULT TRUE,
                max_tool_calls INTEGER DEFAULT 80,
                connected_tools TEXT DEFAULT '[]',
                llm_config_id INTEGER,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_documents (
                id SERIAL PRIMARY KEY,
                doc_id INTEGER REFERENCES knowledge_base(id) ON DELETE CASCADE,
                agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                embedding vector(768)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_threads (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
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
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                steps TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
                status TEXT NOT NULL,
                logs TEXT DEFAULT '[]',
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        ''')

        # Run Alter statements to add organization_id and user_id column if tables were created previously
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE workflows ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE tool_credentials ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS sync_status TEXT DEFAULT 'processing'")
        cursor.execute("ALTER TABLE workflows ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft'")
        
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE llm_config ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE tool_credentials ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
        cursor.execute("SELECT 1 FROM pg_constraint WHERE conname = 'unique_user_tool'")
        if not cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE tool_credentials ADD CONSTRAINT unique_user_tool UNIQUE (user_id, tool_name)")
            except Exception:
                pass
        try:
            cursor.execute("ALTER TABLE tool_credentials DROP CONSTRAINT IF EXISTS tool_credentials_tool_name_key CASCADE")
        except Exception as e:
            print("Could not drop constraint tool_credentials_tool_name_key:", e)
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS user_prompt TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS creativity REAL DEFAULT 0.5")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS guardrails BOOLEAN DEFAULT TRUE")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS max_tool_calls INTEGER DEFAULT 80")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS guardrail_types TEXT DEFAULT '[]'")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE workflows ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE")
        cursor.execute("ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE")
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
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT DEFAULT '',
                user_prompt TEXT DEFAULT '',
                creativity REAL DEFAULT 0.5,
                guardrails BOOLEAN DEFAULT 1,
                max_tool_calls INTEGER DEFAULT 80,
                connected_tools TEXT DEFAULT '[]',
                llm_config_id INTEGER,
                is_default BOOLEAN DEFAULT 0,
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
                project_id INTEGER,
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
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_id INTEGER,
                agent_id INTEGER,
                name TEXT NOT NULL,
                steps TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                workflow_id INTEGER,
                status TEXT NOT NULL,
                logs TEXT DEFAULT '[]',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
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
        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN project_id INTEGER")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE workflows ADD COLUMN project_id INTEGER")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE chat_threads ADD COLUMN project_id INTEGER")
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE agents ADD COLUMN is_default BOOLEAN DEFAULT 0")
        except Exception:
            pass

    conn.commit()

    # Create default projects for users
    try:
        if USE_POSTGRES:
            cursor.execute("SELECT id FROM users")
            users = cursor.fetchall()
            for user in users:
                cursor.execute("SELECT id FROM projects WHERE user_id = %s", (user[0],))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO projects (user_id, name, description) VALUES (%s, %s, %s)", (user[0], "Default Project", "Default workspace"))
            
            # Map orphaned items
            cursor.execute("UPDATE agents SET project_id = (SELECT id FROM projects WHERE projects.user_id = agents.user_id LIMIT 1) WHERE project_id IS NULL")
            cursor.execute("UPDATE workflows SET project_id = (SELECT id FROM projects WHERE projects.user_id = workflows.user_id LIMIT 1) WHERE project_id IS NULL")
            cursor.execute("UPDATE chat_threads SET project_id = (SELECT id FROM projects WHERE projects.user_id = chat_threads.user_id LIMIT 1) WHERE project_id IS NULL")
            
        else:
            cursor.execute("SELECT id FROM users")
            users = cursor.fetchall()
            for user in users:
                cursor.execute("SELECT id FROM projects WHERE user_id = ?", (user[0],))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)", (user[0], "Default Project", "Default workspace"))
            
            # Map orphaned items
            cursor.execute("UPDATE agents SET project_id = (SELECT id FROM projects WHERE projects.user_id = agents.user_id LIMIT 1) WHERE project_id IS NULL")
            cursor.execute("UPDATE workflows SET project_id = (SELECT id FROM projects WHERE projects.user_id = workflows.user_id LIMIT 1) WHERE project_id IS NULL")
            cursor.execute("UPDATE chat_threads SET project_id = (SELECT id FROM projects WHERE projects.user_id = chat_threads.user_id LIMIT 1) WHERE project_id IS NULL")
            
        conn.commit()
    except Exception as e:
        print(f"[DB] Error mapping default projects: {e}")

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
    cur = conn.cursor()
    try:
        # Insert User
        cur.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, email, password_hash, role)
        )
        user_id = cur.fetchone()[0]
        
        # Create Default Organization
        org_name = f"{username}'s Workspace"
        cur.execute(
            "INSERT INTO organizations (name) VALUES (%s) RETURNING id",
            (org_name,)
        )
        org_id = cur.fetchone()[0]
        
        # Map user to organization as Admin
        cur.execute(
            "INSERT INTO organization_users (organization_id, user_id, role) VALUES (%s, %s, %s)",
            (org_id, user_id, 'admin')
        )
        
        conn.commit()
        return {"id": user_id, "username": username, "email": email, "role": role, "default_org_id": org_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_conn()
    cur = _execute(conn, "SELECT * FROM users WHERE username = %s", (username,))
    user = _fetchone_as_dict(cur)
    conn.close()
    return user

def get_user_organizations(user_id):
    conn = get_conn()
    cur = _execute(conn, '''
        SELECT o.id, o.name, ou.role 
        FROM organizations o
        JOIN organization_users ou ON o.id = ou.organization_id
        WHERE ou.user_id = %s
    ''', (user_id,))
    orgs = _fetchall_as_dicts(cur)
    conn.close()
    return orgs

def get_user(user_id):
    conn = get_conn()
    cur = _execute(conn, "SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
    row = _fetchone_as_dict(cur)
    conn.close()
    return row

# --- Agent CRUD ---

def create_agent(user_id, project_id, name, description, system_prompt="", user_prompt="", creativity=0.5, guardrails=True, max_tool_calls=80, connected_tools=None, llm_config_id=None, guardrail_types=None):
    if connected_tools is None:
        connected_tools = []
    if guardrail_types is None:
        guardrail_types = []
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 
            'INSERT INTO agents (user_id, project_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, connected_tools, llm_config_id, guardrail_types) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (user_id, project_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, json.dumps(connected_tools), llm_config_id, json.dumps(guardrail_types)))
        agent_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO agents (user_id, project_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, connected_tools, llm_config_id, guardrail_types) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, project_id, name, description, system_prompt, user_prompt, creativity, guardrails, max_tool_calls, json.dumps(connected_tools), llm_config_id, json.dumps(guardrail_types)))
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

def set_default_agent(user_id, project_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    if USE_POSTGRES:
        _execute(conn, 'UPDATE agents SET is_default = FALSE WHERE user_id = %s AND project_id = %s', (user_id, project_id))
        _execute(conn, 'UPDATE agents SET is_default = TRUE WHERE user_id = %s AND project_id = %s AND id = %s', (user_id, project_id, agent_id))
    else:
        _execute(conn, 'UPDATE agents SET is_default = 0 WHERE user_id = ? AND project_id = ?', (user_id, project_id))
        _execute(conn, 'UPDATE agents SET is_default = 1 WHERE user_id = ? AND project_id = ? AND id = ?', (user_id, project_id, agent_id))
    conn.commit()
    conn.close()

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
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content, sync_status) VALUES (%s, %s, %s, %s) RETURNING id', (agent_id, filename, content, 'processing'))
        kb_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO knowledge_base (agent_id, filename, content, sync_status) VALUES (?, ?, ?, ?)', (agent_id, filename, content, 'processing'))
        kb_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": kb_id, "agent_id": agent_id, "filename": filename, "sync_status": "processing"}

def get_knowledge(user_id, agent_id):
    if not verify_agent_ownership(user_id, agent_id):
        return []
    conn = get_conn()
    cur = _execute(conn, 'SELECT id, filename, uploaded_at, sync_status FROM knowledge_base WHERE agent_id = %s' if USE_POSTGRES else 'SELECT id, filename, uploaded_at, sync_status FROM knowledge_base WHERE agent_id = ?', (agent_id,))
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

def create_chat_thread(user_id, agent_id, title, project_id):
    if agent_id is not None and not verify_agent_ownership(user_id, agent_id):
        raise PermissionError("User does not own this agent")
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn, 'INSERT INTO chat_threads (user_id, agent_id, title, project_id) VALUES (%s, %s, %s, %s) RETURNING id', (user_id, agent_id, title, project_id))
        thread_id = cur.fetchone()[0]
    else:
        cur = _execute(conn, 'INSERT INTO chat_threads (user_id, agent_id, title, project_id) VALUES (?, ?, ?, ?)', (user_id, agent_id, title, project_id))
        thread_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": thread_id, "user_id": user_id, "agent_id": agent_id, "title": title, "project_id": project_id}

def get_chat_threads(user_id, agent_id=None, project_id=None):
    conn = get_conn()
    if USE_POSTGRES:
        if agent_id is not None:
            cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = %s AND agent_id = %s AND project_id = %s ORDER BY id DESC', (user_id, agent_id, project_id))
        else:
            cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = %s AND project_id = %s ORDER BY id DESC', (user_id, project_id))
    else:
        if agent_id is not None:
            cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = ? AND agent_id = ? AND project_id = ? ORDER BY id DESC', (user_id, agent_id, project_id))
        else:
            cur = _execute(conn, 'SELECT * FROM chat_threads WHERE user_id = ? AND project_id = ? ORDER BY id DESC', (user_id, project_id))
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


current_connection_id = contextvars.ContextVar("current_connection_id", default=None)

def get_tool_connections(user_id, tool_name):
    if user_id is None:
        user_id = current_user_id.get()
    conn = get_conn()
    cur = _execute(conn, 'SELECT credentials FROM tool_credentials WHERE user_id = ? AND tool_name = ?', (user_id, tool_name.lower()))
    row = _fetchone_as_dict(cur)
    conn.close()
    if not row:
        return []
    try:
        data = json.loads(row["credentials"])
        if isinstance(data, dict) and "connections" in data:
            return data["connections"]
        # Legacy format support
        if data and isinstance(data, dict):
            if "username" in data or "instance_url" in data:
                legacy = {"id": "default", "name": "Default Connection"}
                legacy.update(data)
                return [legacy]
    except Exception as e:
        print(f"Error parsing connections: {e}")
    return []

def save_tool_connection(user_id, tool_name, connection_data):
    if user_id is None:
        user_id = current_user_id.get()
    
    connections = get_tool_connections(user_id, tool_name)
    conn_id = connection_data.get("id")
    if not conn_id:
        import uuid
        conn_id = "conn_" + str(uuid.uuid4())[:8]
        connection_data["id"] = conn_id
    
    # Update or append
    updated = False
    for i, c in enumerate(connections):
        if c.get("id") == conn_id:
            connections[i] = connection_data
            updated = True
            break
    if not updated:
        connections.append(connection_data)
        
    payload = {"connections": connections}
    save_credentials(user_id, tool_name.lower(), payload)
    return connection_data

def delete_tool_connection(user_id, tool_name, connection_id):
    if user_id is None:
        user_id = current_user_id.get()
    connections = get_tool_connections(user_id, tool_name)
    connections = [c for c in connections if c.get("id") != connection_id]
    payload = {"connections": connections}
    save_credentials(user_id, tool_name.lower(), payload)
    return True

def get_credentials(user_id, tool_name):
    if user_id is None:
        user_id = current_user_id.get()
    tool_name = tool_name.lower()
    print(f"[DB Debug] get_credentials for {tool_name}: user_id={user_id}, ContextVar={current_user_id.get()}, connection_id={current_connection_id.get()}")
    conn = get_conn()
    cur = _execute(conn, 'SELECT credentials FROM tool_credentials WHERE user_id = ? AND tool_name = ?', (user_id, tool_name))
    row = _fetchone_as_dict(cur)
    conn.close()
    if not row:
        return {}
    try:
        data = json.loads(row["credentials"])
        if isinstance(data, dict) and "connections" in data:
            connections = data["connections"]
            selected_id = current_connection_id.get()
            if selected_id:
                for c in connections:
                    if c.get("id") == selected_id or c.get("name") == selected_id:
                        return c
            # Fallback to the first connection if none selected
            if connections:
                return connections[0]
            return {}
        return data
    except Exception as e:
        print(f"[DB Debug] error in get_credentials: {e}")
        return {}


# --- LLM Config CRUD (Encrypted) ---

def add_llm_config(user_id, provider, model_name, api_key, project_id=None):
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
    return {"id": config_id, "project_id": project_id, "provider": provider, "model_name": model_name, "api_key_masked": mask_key(api_key)}

def get_all_llm_configs(user_id, project_id=None):
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

def create_workflow(user_id, agent_id, name, steps, status="draft", project_id=None):
    if agent_id is not None:
        if not verify_agent_ownership(user_id, agent_id):
            raise PermissionError("User does not own this agent")
    conn = get_conn()
    steps_str = json.dumps(steps) if isinstance(steps, (dict, list)) else steps
    if USE_POSTGRES:
        cur = _execute(conn,
            'INSERT INTO workflows (user_id, agent_id, project_id, name, steps, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
            (user_id, agent_id, project_id, name, steps_str, status))
        wf_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO workflows (user_id, agent_id, project_id, name, steps, status) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, agent_id, project_id, name, steps_str, status))
        wf_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": wf_id, "user_id": user_id, "agent_id": agent_id, "project_id": project_id, "name": name, "steps": steps, "status": status}

def update_workflow(user_id, workflow_id, name, steps, status="draft"):
    conn = get_conn()
    steps_str = json.dumps(steps) if isinstance(steps, (dict, list)) else steps
    
    # Verify ownership
    cur = _execute(conn, 'SELECT id FROM workflows WHERE id = ? AND user_id = ?', (workflow_id, user_id))
    if not cur.fetchone():
        conn.close()
        raise PermissionError("User does not own this workflow")
        
    if USE_POSTGRES:
        _execute(conn,
            'UPDATE workflows SET name = %s, steps = %s, status = %s WHERE id = %s',
            (name, steps_str, status, workflow_id))
    else:
        _execute(conn,
            'UPDATE workflows SET name = ?, steps = ?, status = ? WHERE id = ?',
            (name, steps_str, status, workflow_id))
            
    conn.commit()
    conn.close()
    return {"id": workflow_id, "name": name, "steps": steps, "status": status}

def get_workflows(user_id, agent_id=None, project_id=None):
    conn = get_conn()
    
    if USE_POSTGRES:
        if agent_id:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = %s AND agent_id = %s ORDER BY created_at DESC', (user_id, agent_id))
        elif project_id:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = %s AND project_id = %s ORDER BY created_at DESC', (user_id, project_id))
        else:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    else:
        if agent_id:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? AND agent_id = ? ORDER BY created_at DESC', (user_id, agent_id))
        elif project_id:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? AND project_id = ? ORDER BY created_at DESC', (user_id, project_id))
        else:
            cur = _execute(conn, 'SELECT * FROM workflows WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            
    rows = _fetchall_as_dicts(cur)
    conn.close()
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
    if USE_POSTGRES:
        _execute(conn, 'DELETE FROM workflows WHERE user_id = %s AND id = %s', (user_id, workflow_id))
    else:
        _execute(conn, 'DELETE FROM workflows WHERE user_id = ? AND id = ?', (user_id, workflow_id))
    conn.commit()
    conn.close()

# --- Workflow Runs ---

def create_workflow_run(user_id, workflow_id, status="running"):
    conn = get_conn()
    if USE_POSTGRES:
        cur = _execute(conn,
            'INSERT INTO workflow_runs (user_id, workflow_id, status) VALUES (%s, %s, %s) RETURNING id',
            (user_id, workflow_id, status))
        run_id = cur.fetchone()[0]
    else:
        cur = _execute(conn,
            'INSERT INTO workflow_runs (user_id, workflow_id, status) VALUES (?, ?, ?)',
            (user_id, workflow_id, status))
        run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_workflow_status(user_id, workflow_id, status):
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
    conn.close()
    return {"id": workflow_id, "status": status}

def update_workflow_run(run_id, status, logs):
    conn = get_conn()
    logs_str = json.dumps(logs) if isinstance(logs, (dict, list)) else logs
    if USE_POSTGRES:
        _execute(conn,
            'UPDATE workflow_runs SET status = %s, logs = %s, completed_at = NOW() WHERE id = %s',
            (status, logs_str, run_id))
    else:
        _execute(conn,
            'UPDATE workflow_runs SET status = ?, logs = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, logs_str, run_id))
    conn.commit()
    conn.close()

def get_workflow_runs(user_id, workflow_id=None, status=None, project_id=None):
    conn = get_conn()
    query = 'SELECT * FROM workflow_runs WHERE user_id = ' + ('%s' if USE_POSTGRES else '?')
    params = [user_id]
    
    if workflow_id:
        query += ' AND workflow_id = ' + ('%s' if USE_POSTGRES else '?')
        params.append(workflow_id)
    if status:
        query += ' AND status = ' + ('%s' if USE_POSTGRES else '?')
        params.append(status)
    if project_id and not workflow_id:
        query += ' AND workflow_id IN (SELECT id FROM workflows WHERE project_id = ' + ('%s' if USE_POSTGRES else '?') + ')'
        params.append(project_id)
        
    query += ' ORDER BY started_at DESC LIMIT 100'
    
    cur = _execute(conn, query, tuple(params))
    rows = _fetchall_as_dicts(cur)
    conn.close()
    
    for row in rows:
        try:
            row["logs"] = json.loads(row["logs"])
        except Exception:
            row["logs"] = []
    return rows

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

