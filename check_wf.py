import sqlite3
conn = sqlite3.connect(r'c:\Users\Admin\Documents\Agentic AI\backend\agentic.db')
cur = conn.cursor()
cur.execute('SELECT id, name, agent_id FROM workflows')
rows = cur.fetchall()
print('Workflows:', rows)
