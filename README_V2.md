
AGENT AI - V2 COMPLETE WORKFLOW AUTOMATION PLATFORM
=====================================================

BUILT WITH:
- Frontend: React 19 + TypeScript + React Flow + Tailwind CSS
- Backend: FastAPI + Celery + Redis
- Architecture: DAG-based workflow execution with 15+ integrations

====== KEY FEATURES ======

1. WORKFLOW EDITOR (React Flow Canvas)
   - Drag-and-drop piece library (15+ integrations)
   - Visual node connections with React Flow
   - Color-coded by category (Triggers, Email, Communication, etc.)
   - Node configuration panel on right
   - Execution order via topological sort

2. AVAILABLE PIECES/INTEGRATIONS

   TRIGGERS:
   - Manual Trigger (start workflows manually)
   - Webhook Trigger (trigger from HTTP calls)
   - Schedule Trigger (cron-based scheduling)

   EMAIL:
   - Gmail (send emails via Gmail)
   - SMTP (send emails via SMTP)

   COMMUNICATION:
   - Slack (send Slack messages)
   - Discord (send Discord messages)
   - Telegram (send Telegram messages)

   PROJECT MANAGEMENT:
   - Jira (create/update issues)
   - Asana (create/manage tasks)
   - Monday.com (manage board items)

   CRM:
   - Salesforce (create records)
   - HubSpot (manage contacts/deals)

   DATABASE:
   - Airtable (create/update records)
   - MongoDB (store data)

   LOGIC:
   - If/Else Condition (branching logic)
   - Loop Action (iterate over arrays)
   - Delay/Wait (pause execution)

3. WORKFLOW EXECUTION
   - Topological sort for execution order (respects dependencies)
   - Cycle detection (prevents infinite loops)
   - Execution history tracking
   - Real-time execution status

4. PROJECT MANAGEMENT
   - Create multiple projects/workspaces
   - Save workflows with node configurations
   - Execution history per project
   - In-memory storage for testing

5. AUTHENTICATION
   - Username/password login
   - Token-based auth (JWT)
   - Signup for new users
   - Test user: test/test123

====== SETUP INSTRUCTIONS ======

STEP 1: Build Frontend
  cd "c:\Users\Admin\Documents\Agentic AI\v2\frontend"
  npm install
  npm run build

STEP 2: Install Backend
  cd "c:\Users\Admin\Documents\Agentic AI\v2\backend"
  pip install -r requirements.txt

STEP 3: Start Backend
  cd "c:\Users\Admin\Documents\Agentic AI\v2\backend"
  python -m uvicorn main_simple:app --reload --port 8000

STEP 4: Open Browser
  http://localhost:8000/

STEP 5: Login
  Username: test
  Password: test123

====== USAGE FLOW ======

1. LOGIN
   - Use test/test123 or create new account

2. DASHBOARD
   - View existing projects
   - Click project to edit
   - Create new project with "New Project" button

3. WORKFLOW EDITOR
   - Left panel: Piece library (searchable)
   - Click piece to add to canvas
   - Connect pieces by dragging edges
   - Right panel: Configure selected node

4. NODE CONFIGURATION
   - Select node to see properties
   - Edit piece name
   - Add piece-specific configuration (API keys, fields, etc.)
   - Delete node with trash icon

5. EXECUTE WORKFLOW
   - Click "Execute" button to run workflow
   - View execution history in right panel
   - Check results for each node

====== BACKEND ENDPOINTS ======

AUTH:
  POST /api/auth/login
  POST /api/auth/register

PROJECTS:
  GET /api/agents
  POST /api/agents
  GET /api/agents/{id}

WORKFLOWS:
  POST /api/workflows/execute
  POST /api/workflows/{id}
  GET /api/nodes/schema

EXECUTION:
  GET /api/history
  GET /api/health
  WS /ws/logs

====== FILE STRUCTURE ======

v2/frontend/
  src/
    pages/
      Login.tsx         - Authentication page
      Signup.tsx        - Registration page
      Dashboard.tsx     - Project listing/creation
      Project.tsx       - Workflow editor
    components/
      ExecutionHistory.tsx - Execution history viewer
    App.tsx             - Router and auth logic

v2/backend/
  main_simple.py        - FastAPI server (no Redis needed)
  main.py               - Production server (requires Redis)
  schemas.py            - Pydantic models and piece definitions
  tasks.py              - Celery workflow executor
  db.py                 - SQLite persistence
  celery_app.py         - Celery configuration
  requirements.txt      - Python dependencies

====== TESTING WORKFLOW ======

1. Create project
2. Add Manual Trigger
3. Add Gmail action (configure with test email)
4. Connect Trigger to Gmail with edge
5. Click Execute
6. Check execution history for results

====== TROUBLESHOOTING ======

npm not in PATH?
  - Make sure Node.js is installed
  - Add to PATH or use full path: C:\Program Files\nodejs\npm.cmd

Redis not running?
  - Use main_simple.py instead of main.py
  - Install Redis via Docker/WSL for production

Frontend not loading?
  - Ensure npm run build completed
  - Check that dist/ folder exists
  - Restart backend server

====== NEXT STEPS ======

1. Add Redis + Celery worker for real async execution
2. Implement piece configurations in database
3. Add user authentication tokens to database
4. Connect to real APIs (Gmail, Slack, Jira, etc.)
5. Add execution logs viewer
6. Implement piece marketplace UI

====== DEVELOPMENT ======

Frontend dev mode:
  cd v2/frontend
  npm run dev

Watch backend:
  cd v2/backend
  python -m uvicorn main_simple:app --reload

Debug workflow:
  - Check console logs in browser
  - Check terminal output from backend
  - Review execution history for errors

