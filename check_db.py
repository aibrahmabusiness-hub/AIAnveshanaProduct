import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Admin\Documents\Agentic AI\backend\.env")
db_url = os.getenv("DATABASE_URL")
if db_url:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, status, agent_id, user_id FROM workflows")
    rows = cur.fetchall()
    print("Workflows in Postgres:")
    for r in rows:
        print(r)
else:
    print("No DATABASE_URL found.")
