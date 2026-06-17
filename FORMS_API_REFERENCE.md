# FORM VALIDATION & API ENDPOINTS REFERENCE

## AUTHENTICATION FORMS

### 1. LOGIN FORM

#### Legacy Implementation (frontend/login.html)
```html
<form id="loginForm">
  <div class="form-group">
    <label for="username">Username</label>
    <input type="text" id="username" required placeholder="admin" autofocus>
  </div>
  <div class="form-group">
    <label for="password">Password</label>
    <input type="password" id="password" required placeholder="••••••••">
  </div>
  <button type="submit" class="auth-btn">Sign In</button>
</form>
```

**JavaScript Validation:**
```javascript
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  const res = await fetch(API_BASE_URL + '/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Login failed');
  }
  
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  if (data.ap_token) localStorage.setItem('ap_token', data.ap_token);
  if (data.ap_projectId) localStorage.setItem('ap_projectId', data.ap_projectId);
  localStorage.setItem('username', username);
  window.location.href = '/';
});
```

**Error Handling:**
- Displays error in `.error-message` div with error.detail text
- Hidden by default, shown only on error

#### React Implementation (v2/frontend/src/pages/Login.tsx)
```typescript
const [username, setUsername] = useState('');
const [password, setPassword] = useState('');
const [errorMsg, setErrorMsg] = useState('');
const [isLoading, setIsLoading] = useState(false);

const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  setErrorMsg('');
  setIsLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    if (data.ap_token) localStorage.setItem('ap_token', data.ap_token);
    if (data.ap_projectId) localStorage.setItem('ap_projectId', data.ap_projectId);
    localStorage.setItem('username', username);
    
    navigate('/');
  } catch (err: any) {
    setErrorMsg(err.message);
  } finally {
    setIsLoading(false);
  }
};
```

**Comparison:**
| Aspect | Legacy | React |
|--------|--------|-------|
| Validation | HTML5 required attr | HTML5 + controlled inputs |
| Error Display | Manual DOM manipulation | State-based rendering |
| Loading State | Not visible | Button disabled + text change |
| State Management | DOM state | React useState hooks |
| API Call | Fetch in event listener | Fetch in async handler |

**API Endpoint:**
```
POST /api/auth/login
Content-Type: application/json

Request Body:
{
  "username": "admin",
  "password": "password123"
}

Response (200 OK):
{
  "access_token": "eyJhbGc...",
  "ap_token": "optional_token",
  "ap_projectId": "optional_project_id"
}

Response (4xx/5xx):
{
  "detail": "Invalid username or password"
}
```

**LocalStorage Keys Set:**
- `token`: JWT access token
- `ap_token`: Optional API platform token
- `ap_projectId`: Optional default project ID
- `username`: Username for display

---

### 2. SIGNUP FORM

#### Legacy Implementation (frontend/signup.html)
```html
<form id="signupForm">
  <div class="form-group">
    <label for="username">Username</label>
    <input type="text" id="username" required placeholder="john_doe" autofocus>
  </div>
  <div class="form-group">
    <label for="email">Email (Optional)</label>
    <input type="email" id="email" placeholder="john@example.com">
  </div>
  <div class="form-group">
    <label for="password">Password</label>
    <input type="password" id="password" required placeholder="••••••••">
  </div>
  <button type="submit" class="auth-btn">Sign Up</button>
</form>
```

**JavaScript Validation:**
```javascript
signupForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value;
  const email = document.getElementById('email').value || null;
  const password = document.getElementById('password').value;
  
  const res = await fetch(API_BASE_URL + '/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Registration failed');
  }
  
  // Show success message, redirect after 1.5s
  successMsg.style.display = 'block';
  setTimeout(() => {
    window.location.href = '/login';
  }, 1500);
});
```

#### React Implementation (v2/frontend/src/pages/Signup.tsx)
```typescript
const [username, setUsername] = useState('');
const [password, setPassword] = useState('');
const [errorMsg, setErrorMsg] = useState('');
const [successMsg, setSuccessMsg] = useState('');
const [isLoading, setIsLoading] = useState(false);

const handleSignup = async (e: React.FormEvent) => {
  e.preventDefault();
  setErrorMsg('');
  setSuccessMsg('');
  setIsLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Signup failed');
    }
    
    setSuccessMsg('Account created successfully! Redirecting to login...');
    setTimeout(() => {
      navigate('/login');
    }, 2000);
  } catch (err: any) {
    setErrorMsg(err.message);
  } finally {
    setIsLoading(false);
  }
};
```

**Comparison:**
| Aspect | Legacy | React |
|--------|--------|-------|
| Email Field | Yes (optional) | NO (removed) |
| Validation | HTML5 type="email" + required | HTML5 + controlled inputs |
| Success UX | Show message + 1.5s redirect | Show message + 2s redirect |
| Button State | No disable on submit | Button disabled during request |

**BREAKING CHANGE:** Email field removed in React version - needs migration decision

**API Endpoint:**
```
POST /api/auth/register
Content-Type: application/json

Request Body (Legacy):
{
  "username": "john_doe",
  "email": "john@example.com",    // Optional
  "password": "password123"
}

Request Body (React):
{
  "username": "john_doe",
  "password": "password123"
}

Response (200 OK):
{
  "id": "user_id",
  "username": "john_doe"
}

Response (409 Conflict):
{
  "detail": "Username already exists"
}
```

---

## DASHBOARD FORMS

### 3. CREATE PROJECT FORM

#### Legacy Implementation (frontend/index.html Modal)
```html
<div class="modal-overlay" id="createModal">
  <div class="modal" style="width:480px;">
    <div class="modal-header">
      <h3>Create New Agent Project</h3>
      <button class="close-btn" id="closeModalBtn">&times;</button>
    </div>
    <form id="createProjectForm">
      <div class="form-group">
        <label>Project Name</label>
        <input type="text" id="projectName" required placeholder="e.g. IT Issue Resolver">
      </div>
      <div class="form-group">
        <label>Description</label>
        <input type="text" id="projectDesc" required placeholder="e.g. Resolves IT tickets via email">
      </div>
      <div class="form-group">
        <label>Agent System Prompt</label>
        <textarea id="systemPrompt" rows="4" 
          placeholder="You are an IT support agent..."></textarea>
      </div>
      <div class="form-group">
        <label>Connect Tools</label>
        <div id="toolCheckboxes">
          <!-- Populated by JS -->
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn-cancel" id="cancelModalBtn">Cancel</button>
        <button type="submit" class="btn-primary">Create Agent</button>
      </div>
    </form>
  </div>
</div>
```

**Fields:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Project Name | text | Yes | Free text input |
| Description | text | Yes | Free text input |
| System Prompt | textarea | Implied | AI agent instructions |
| Tools | checkboxes | No | Multi-select tool bindings |

#### React Implementation
**Status: NOT YET IMPLEMENTED** - Missing from v2/frontend/src/pages/Dashboard.tsx

**Required Implementation:**
- Modal component or dialog
- Form fields matching legacy
- Tool checkbox selection (requires schema from `/api/nodes/schema`)
- POST request to create agent

---

## PROJECT EDITOR FORMS

### 4. NODE CONFIGURATION (PROJECT.HTML)

#### Legacy: DrawFlow Nodes
- Dynamic forms based on node type
- Guardrail configuration checkboxes
- Config stored in DrawFlow node data

#### React: ReactFlow Nodes
- BaseNode component for rendering
- Node types: trigger_manual, trigger_webhook, action_gmail, action_slack, action_jira, action_salesforce
- Config stored in Redux/Zustand store
- No configuration UI visible in current implementation

---

## API ENDPOINTS SUMMARY

### Authentication Endpoints
| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/api/auth/login` | POST | No | User login |
| `/api/auth/register` | POST | No | User registration |

### Agent Management
| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/api/agents` | GET | Yes | List user's agents |
| `/api/agents` | POST | Yes | Create new agent (inferred) |
| `/api/agents/{id}` | GET | Yes | Get agent details (inferred) |
| `/api/agents/{id}` | PUT | Yes | Update agent (inferred) |
| `/api/agents/{id}` | DELETE | Yes | Delete agent (inferred) |

### Workflow/Node Endpoints
| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/api/nodes/schema` | GET | No | Get available node types and schema |

### Real-time Endpoints
| Endpoint | Type | Purpose |
|----------|------|---------|
| `/ws/logs` | WebSocket | Real-time node execution status |

---

## AUTHENTICATION & STORAGE

### localStorage Keys
After successful login, these are set:
```javascript
localStorage.setItem('token', data.access_token);          // JWT token
localStorage.setItem('ap_token', data.ap_token);           // Optional
localStorage.setItem('ap_projectId', data.ap_projectId);   // Optional
localStorage.setItem('username', username);                // Display name
```

### Route Protection Pattern
**Legacy:**
```javascript
if (!localStorage.getItem('token')) {
  window.location.href = '/login';
}
```

**React:**
```typescript
useEffect(() => {
  const token = localStorage.getItem('token');
  if (!token) {
    navigate('/login');
    return;
  }
}, [navigate]);
```

### Authorization Headers
All authenticated requests must include:
```
Authorization: Bearer <token>
```

---

## ERROR HANDLING PATTERNS

### Legacy
```javascript
try {
  const res = await fetch(...);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Operation failed');
  }
  // ...
} catch (err) {
  errorMsg.textContent = err.message;
  errorMsg.style.display = 'block';
}
```

### React
```typescript
try {
  const res = await fetch(...);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Operation failed');
  }
  // ...
} catch (err: any) {
  setErrorMsg(err.message);
}
```

---

## MIGRATION CHECKLIST

### Authentication
- [x] Login form (functional)
- [x] Signup form (functional, but email removed)
- [ ] Password reset (not implemented anywhere)
- [ ] Email verification (not implemented anywhere)
- [ ] Session refresh/token expiration

### Dashboard
- [ ] List agents API integration (basic structure exists)
- [ ] Create agent modal and form
- [ ] Edit agent (inferred from schema)
- [ ] Delete agent (inferred from schema)
- [ ] Search/filter projects

### Project Editor
- [ ] Node schema fetching (implemented)
- [ ] Node configuration UI (missing)
- [ ] Save/publish workflow
- [ ] Test workflow
- [ ] WebSocket status updates (framework implemented)

### Error Handling
- [ ] 401 Unauthorized - redirect to login
- [ ] 403 Forbidden - show access denied
- [ ] 404 Not Found - show not found
- [ ] 5xx Server Error - show retry message
- [ ] Network errors - show offline message

### Security
- [ ] CORS configuration
- [ ] CSRF protection if needed
- [ ] Rate limiting awareness
- [ ] API key rotation (if applicable)

---

## TESTING REQUIREMENTS

### Manual Testing Endpoints
```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password","email":"user@example.com"}'

# Test agents list (with token)
curl -X GET http://localhost:8000/api/agents \
  -H "Authorization: Bearer <token>"

# Test schema
curl -X GET http://localhost:8000/api/nodes/schema

# Test WebSocket
websocat ws://localhost:8000/ws/logs
```

---

## Frontend <-> Backend Integration Notes

1. **Base URL**: React hardcoded to `http://localhost:8000`, should use env variable
2. **CORS**: May need to handle CORS headers from backend
3. **Token Refresh**: No token refresh logic implemented
4. **Logout**: Clears localStorage but no backend logout endpoint called
5. **Error Handling**: Assumes backend returns `{ detail: "error message" }` format
6. **Real-time Updates**: WebSocket implementation assumes server sends `{ node_id, status }` messages
