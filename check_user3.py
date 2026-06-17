import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Admin\Documents\Agentic AI\backend\.env")
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT * FROM workflows WHERE user_id = 3")
rows = cur.fetchall()
print("user_id 3 workflows:", rows)
