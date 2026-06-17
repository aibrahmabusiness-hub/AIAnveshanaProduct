import sys
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.append('backend')
from database import get_conn, _execute

try:
    conn = get_conn()
    _execute(conn, 'ALTER TABLE llm_config ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE', ())
    conn.commit()
    conn.close()
    print('Column project_id added to llm_config successfully.')
except Exception as e:
    err_msg = str(e).lower()
    if 'duplicate column' in err_msg or 'already exists' in err_msg or 'column "project_id"' in err_msg:
        print('Column already exists.')
    else:
        print(f'Error: {e}')
