import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from database import get_conn

try:
    conn = get_conn()
    cur = conn.cursor()
    print("Connected to database successfully.")
    
    # Let's check existing constraints on tool_credentials
    cur.execute("""
        SELECT conname, contype 
        FROM pg_constraint 
        WHERE conrelid = 'tool_credentials'::regclass;
    """)
    constraints = cur.fetchall()
    print("Existing constraints:", constraints)
    
    # Let's drop the constraint
    print("Dropping constraint tool_credentials_tool_name_key...")
    cur.execute("ALTER TABLE tool_credentials DROP CONSTRAINT IF EXISTS tool_credentials_tool_name_key CASCADE;")
    
    # Check constraints again
    cur.execute("""
        SELECT conname, contype 
        FROM pg_constraint 
        WHERE conrelid = 'tool_credentials'::regclass;
    """)
    constraints_after = cur.fetchall()
    print("Constraints after dropping:", constraints_after)
    
    conn.commit()
    print("Transaction committed.")
    conn.close()
    print("Done!")
except Exception as e:
    traceback.print_exc()
