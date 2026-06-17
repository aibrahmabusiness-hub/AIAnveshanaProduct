# 🚀 QUICK START - Get http://localhost:8001/ Working in 3 Steps

## Step 1: Install Dependencies

### Backend (Python)
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\backend
pip install -r requirements.txt
```

### Frontend (Node.js)
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\frontend
npm install
npm run build
```

---

## Step 2: Start Services

### Option A: Manual (Recommended for first time)

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Celery Worker:**
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\backend
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - v2 Backend:**
```bash
cd C:\Users\Admin\Documents\Agentic AI\v2\backend
python -m uvicorn main:app --reload --port 8001
```

---

### Option B: Using Batch Script

Just double-click:
```
C:\Users\Admin\Documents\Agentic AI\v2\start_v2.bat
```

---

## Step 3: Open Browser

**URL:** http://localhost:8001/

---

## ✅ What You Should See

1. **Dashboard loads** with "AI Anveshana" title
2. **Version switcher** appears top-left (shows "Ultra-Lightweight (v2)")
3. **Project cards** appear (if any exist)
4. **New Project** button works

---

## 🐛 Troubleshooting

### "Site can't be reached" or connection refused
- **Check:** Is the backend running? Look for `Uvicorn running on http://0.0.0.0:8001`
- **Check:** Did you build the frontend? Run `npm run build` in `v2/frontend/`
- **Check:** Is the terminal showing errors? Fix any Python import errors

### "Frontend not found" or 404
- **Solution:** Build the frontend:
  ```bash
  cd v2/frontend
  npm run build
  ```
- **Check:** Does `v2/frontend/dist` folder exist?

### Missing dependencies
- **Python:** `pip install -r requirements.txt`
- **Node.js:** `npm install`

### Port already in use
- **Check:** Run `netstat -ano | findstr :8001`
- **Fix:** `taskkill /PID <PID> /F`

---

## 📋 Verify Everything is Working

### 1. Check backend is running:
```bash
curl http://localhost:8001/api/health
```
**Expected:** `{"status":"healthy"}`

### 2. Check frontend is built:
```bash
dir C:\Users\Admin\Documents\Agentic AI\v2\frontend\dist
```
**Expected:** See index.html and other files

### 3. Check Celery is running:
- Look for `celery@your-pc` in the Celery terminal
- Should show `Task ... succeeded` messages

### 4. Check Redis is running:
```bash
redis-cli ping
```
**Expected:** `PONG`

---

## 🎯 What's Running

| Service | Port | Status | URL |
|---------|------|--------|-----|
| v2 Backend | 8001 | ✅ Running | http://localhost:8001/ |
| Celery Worker | N/A | ✅ Running | (background) |
| Redis | 6379 | ✅ Running | (background) |
| Frontend | 8001 | ✅ Served by backend | http://localhost:8001/ |

---

## 📝 Notes

- **v1 is still on port 8000** - Don't stop it, both can run together
- **v2 uses port 8001** - This is the new workflow engine
- **Frontend is built into `dist/`** - The backend serves it automatically
- **Version switcher** - Click to switch between v1 and v2 workflows

---

**✅ That's it! You should now have http://localhost:8001/ working!**
