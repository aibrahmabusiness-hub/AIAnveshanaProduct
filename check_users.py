import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Admin\Documents\Agentic AI\backend\.env")
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT id, username FROM users")
rows = cur.fetchall()
print("Users:", rows)
