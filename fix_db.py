import sys
import os

sys.path.append(r"c:\Users\Admin\Documents\Agentic AI\backend")
from database import get_conn, _execute

def fix_db():
    conn = get_conn()
    try:
        # We must truncate the table to remove 768-dimension vectors before altering the column
        _execute(conn, "TRUNCATE TABLE vector_documents;")
        
        # Alter the embedding column to 1024 dimensions for Mistral
        _execute(conn, "ALTER TABLE vector_documents ALTER COLUMN embedding TYPE vector(1024);")
        
        conn.commit()
        print("Database fixed: vector_documents now supports 1024 dimensions.")
    except Exception as e:
        print(f"Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()
