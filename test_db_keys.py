import sys
sys.path.append('C:/Users/Admin/Documents/Agentic AI/backend')
from database import get_conn, _fetchall_as_dicts

conn = get_conn()
cur = conn.cursor()
cur.execute('SELECT * FROM agents LIMIT 1')
rows = _fetchall_as_dicts(cur)
if rows:
    print("Keys:", rows[0].keys())
else:
    print("No agents in DB")
conn.close()
