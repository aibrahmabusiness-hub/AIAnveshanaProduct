# Running Both v1 and v2 Workflow Engines Simultaneously

## 🎯 Overview

This guide explains how to run **both v1 (legacy) and v2 (new) workflow engines** side-by-side, with a switch in the dashboard to toggle between them.

---

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Redis server

---

## 🚀 Start Both Backends

### Terminal 1: Start v1 Backend (port 8000)
```bash
cd C:\Users\Admin\Documents\Agentic AI\backend
python -m uvicorn main:app --reload --port 8000
```
**Access:** `http://localhost:8000/`

### Terminal 2: Start Redis
```bash
redis-server
```

### Terminal 3: Start Celery Worker for v2
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\backend
celery -A celery_app worker --loglevel=info
```

### Terminal 4: Start v2 Backend (port 8001)
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\backend
python -m uvicorn main:app --reload --port 8001
```
**Access:** `http://localhost:8001/`

### Terminal 5: Build and Serve v2 Frontend
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\frontend
npm install
npm run build
# The built files will be in the 'dist' folder
# The v2 backend will serve them from port 8001
```

---

## 🎨 Access the Unified Dashboard

Once all services are running:

**v2 Dashboard (with version switch):** `http://localhost:8001/`

This dashboard includes:
- ✅ **Version Switcher** (top-right, next to "AI Anveshana")
- ✅ Toggle between:
  - **Legacy (v1)** - Connects to `http://localhost:8000`
  - **Ultra-Lightweight (v2)** - Connects to `http://localhost:8001`

---

## 📊 Version Comparison

| Feature | v1 (Legacy) | v2 (New) |
|---------|-------------|----------|
| **Canvas** | Drawflow (Vanilla JS) | React Flow (xyflow) |
| **State Management** | Custom | Zustand |
| **Styling** | Custom CSS | Tailwind CSS v4 |
| **Execution** | Synchronous | Celery + Redis (Async) |
| **Real-Time** | Polling | WebSocket |
| **DAG Solver** | Custom | graphlib |
| **Dynamic Forms** | ❌ No | ✅ Yes (from Pydantic schemas) |
| **Node Status** | ❌ Static | ✅ Real-time (color-coded) |
| **Execution Logs** | ❌ No | ✅ Yes (live streaming) |

---

## 🔧 Configuration

### v1 Backend (port 8000)
- **Location:** `backend/main.py`
- **API Routes:** `/api/agents/`, `/api/workflows/` (old)
- **Frontend:** Serves old frontend from `frontend/` folder
- **Do NOT modify** - Keep as-is

### v2 Backend (port 8001)
- **Location:** `v2/backend/main.py`
- **API Routes:** `/api/workflows/execute`, `/api/nodes/schema`, `/api/history`
- **Frontend:** Serves new frontend from `v2/frontend/dist/`
- **WebSocket:** `ws://localhost:8001/ws/logs`

---

## 🔄 Version Switch Behavior

When you click the **version switcher** in the dashboard:

1. **Legacy (v1)** selected:
   - API calls go to: `http://localhost:8000`
   - Uses old Drawflow canvas
   - Synchronous execution

2. **Ultra-Lightweight (v2)** selected:
   - API calls go to: `http://localhost:8001`
   - Uses React Flow canvas
   - Async execution with Celery
   - Real-time WebSocket updates

The **preference is saved** in localStorage, so it persists across page refreshes.

---

## 💡 Tips

### If you get CORS errors:
Both backends have CORS enabled for all origins. If you see CORS errors:
1. Make sure both backends are running
2. Check the version switcher shows the correct API URL
3. Clear browser cache

### To check which backend is responding:
```bash
# Check v1
curl http://localhost:8000/api/health

# Check v2
curl http://localhost:8001/api/health
```

### To see WebSocket events:
1. Open browser DevTools (F12)
2. Go to Network → WS (WebSocket)
3. Select the version and click "Execute"
4. Watch real-time events stream in

---

## 🎯 Workflow Endpoints by Version

### v1 (port 8000)
```
GET  /api/agents              - List projects
POST /api/agents              - Create project
GET  /api/agents/{id}         - Get project
GET  /api/workflows/{id}      - Get workflow (old format)
```

### v2 (port 8001)
```
GET  /api/health              - Health check
GET  /api/nodes/schema        - List all pieces
GET  /api/nodes/schema/{name} - Get piece schema
GET  /api/nodes/all-schemas   - Get all schemas
POST /api/workflows/execute   - Execute workflow
GET  /api/history             - Get execution history
WS   /ws/logs                 - Real-time execution logs
```

---

## 🐛 Troubleshooting

### "Connection refused" on port 8001
→ v2 backend is not running. Start it with:
```bash
cd v2/backend && python -m uvicorn main:app --reload --port 8001
```

### "Failed to fetch schema" in v2
→ Make sure v2 backend is running on port 8001

### WebSocket connection fails
→ Check Redis is running: `redis-cli ping` should return "PONG"

### Celery tasks not executing
→ Check Celery worker is running: `celery -A celery_app worker --loglevel=info`

---

## 📝 Summary

✅ **v1 remains untouched on port 8000**
✅ **v2 runs on port 8001**
✅ **v2 frontend has version switcher**
✅ **Both workflow systems work simultaneously**
✅ **No breaking changes to existing functionality**

**You now have both workflow engines running with a convenient switch!** 🎉
