# FRONTEND MIGRATION - QUICK REFERENCE GUIDE

## 📋 DOCUMENT INDEX

1. **MIGRATION_ANALYSIS.md** - Comprehensive comparison of legacy vs React
   - Color schemes, form structure, API endpoints, differences
   - Missing features, tech stack comparison, migration checklist

2. **migration_data.json** - Structured metadata
   - File sizes, component inventory, API endpoint list
   - Migration priorities, tech stack details

3. **COLOR_SCHEME_REFERENCE.md** - Design system deep dive
   - All CSS variables from legacy and React
   - Color comparison tables, implementation recommendations
   - Tailwind theme configuration guidance

4. **FORMS_API_REFERENCE.md** - Form validation & API documentation
   - Detailed form field comparison
   - API endpoint specifications
   - Authentication flow, error handling patterns
   - Testing commands

---

## ⚡ QUICK FACTS

### File Sizes
```
Legacy Total: 130.3 KB
  - login.html: ~4.2 KB
  - signup.html: ~3.8 KB
  - index.html: ~6.5 KB
  - project.html: 59.982 KB
  - style.css: 56.767 KB

React Total: 19.5 KB (85% reduction)
  - Login.tsx: ~2.1 KB
  - Signup.tsx: ~2.3 KB
  - Dashboard.tsx: ~4.5 KB
  - Project.tsx: ~7.4 KB
  - index.css: ~3.2 KB
```

### Color Schemes
```
Legacy: Vibrant Green (#10b981) themed
React: Neutral Navy/Gray (Tailwind default)

Recommendation: Custom Tailwind theme to restore green brand
```

### Tech Stack Evolution
```
Legacy:  HTML5 + Vanilla JS + DrawFlow + CSS Variables
React:   React 18 + TypeScript + @xyflow/react + Tailwind CSS + Zustand
```

---

## 🔑 KEY DIFFERENCES AT A GLANCE

| Aspect | Legacy | React | Status |
|--------|--------|-------|--------|
| **Login Form** | Basic HTML form | Controlled inputs + state | ✅ Same functionality |
| **Signup Form** | With email field | Email field removed | ⚠️ Breaking change |
| **Dashboard** | Grid + search + view toggle | Basic grid only | ⚠️ Features missing |
| **Project Editor** | DrawFlow + config UI | ReactFlow only | ⚠️ Config UI missing |
| **Color Scheme** | Green branded | Neutral gray | ⚠️ Visual change |
| **Build Size** | 130 KB | 19.5 KB | ✅ Much better |

---

## 🎨 DESIGN TOKENS

### Primary Colors
```
Legacy Primary:     #10b981  (Electric Green)
Legacy Dark:        #059669  (Dark Green)
React Primary:      #1e40af  (Navy Blue)

Tailwind Override for Green:
  primary: '#10b981'
  primary-light: '#ecfdf5'
  primary-dark: '#059669'
```

### Neutral Colors
```
Text Primary:       #1e293b  (Slate 900)
Text Secondary:     #64748b  (Slate 500)
Background:         #ffffff  (White)
Card Background:    #ffffff  (White)
Border:             #e2e8f0  (Slate 100)
```

---

## 🔗 API ENDPOINTS

### Implemented
```
POST   /api/auth/login          → Returns access_token
POST   /api/auth/register       → Creates user account
GET    /api/agents              → Lists user's agents
GET    /api/nodes/schema        → Available node types
WS     ws://localhost:8000/ws/logs → Real-time status
```

### Inferred (Not directly referenced)
```
POST   /api/agents              → Create agent
GET    /api/agents/{id}         → Get agent details
PUT    /api/agents/{id}         → Update agent
DELETE /api/agents/{id}         → Delete agent
```

---

## 📝 CRITICAL ISSUES TO RESOLVE

### 🔴 HIGH PRIORITY
1. **Signup Email Field Removed**
   - Legacy: email is optional field
   - React: email field completely removed
   - Action: Restore field OR update backend

2. **Project Creation Modal Missing**
   - Legacy: Full modal with name, description, system prompt, tools
   - React: No modal implemented
   - Action: Implement modal component

3. **Color Scheme Mismatch**
   - Legacy: Green (#10b981) theme throughout
   - React: Navy/gray theme (Tailwind default)
   - Action: Customize Tailwind theme or redesign UI

### 🟡 MEDIUM PRIORITY
1. **Dashboard Features Missing**
   - Search, grid/list toggle, empty state improvements
   - Test workflow, publish buttons

2. **Project Editor Config UI**
   - Node configuration forms missing
   - Guardrail configuration missing

3. **WebSocket Integration**
   - Implemented but needs end-to-end testing
   - Error handling for WebSocket failures

### 🟢 LOW PRIORITY
1. Password reset flow (not in legacy either)
2. Email verification (not in legacy either)
3. Session management/token refresh

---

## 📦 COMPONENT INVENTORY

### Legacy Components
- Header (with logo, profile dropdown)
- Auth Forms (login, signup)
- Project Dashboard (grid, search, toggle)
- Create Project Modal
- Workflow Editor (DrawFlow-based)
- Node Configuration Forms

### React Components
- Header (dashboard only)
- Login Page
- Signup Page
- Dashboard Page
- Project Page (ReactFlow)
- BaseNode (custom node renderer)

### Missing in React
- Reusable Form component
- Modal/Dialog wrapper
- Project creation modal
- Node configuration UI
- Profile dropdown menu

---

## 🧪 TESTING CHECKLIST

### Authentication Flow
- [ ] Can login with valid credentials
- [ ] Shows error on invalid credentials
- [ ] Stores token in localStorage
- [ ] Redirects to dashboard after login
- [ ] Can signup with username/password
- [ ] Shows success message after signup
- [ ] Redirects to login after signup

### Dashboard
- [ ] Can view projects list
- [ ] Shows loading state initially
- [ ] Shows empty state when no projects
- [ ] Can create new project
- [ ] Can search projects
- [ ] Can toggle grid/list view
- [ ] Logout works properly

### Project Editor
- [ ] Can drag nodes from toolbox to canvas
- [ ] Can create connections between nodes
- [ ] Can edit node configuration
- [ ] Real-time status updates show
- [ ] Can test workflow
- [ ] Can publish workflow

### Styling
- [ ] Colors match design system
- [ ] Responsive on mobile/tablet/desktop
- [ ] Dark mode works (if supported)
- [ ] No broken layouts
- [ ] Forms are usable

---

## 🚀 MIGRATION STRATEGY

### Phase 1: Foundation (This Week)
- [ ] Restore email field in Signup (or confirm removal)
- [ ] Customize Tailwind theme with green colors
- [ ] Implement Dashboard project creation modal
- [ ] Complete form validation logic

### Phase 2: Feature Parity (Next Week)
- [ ] Add project search/filter
- [ ] Add grid/list view toggle
- [ ] Implement node configuration UI
- [ ] Add guardrail configuration forms

### Phase 3: Polish (Week After)
- [ ] WebSocket error handling
- [ ] Loading/skeleton states
- [ ] Error message UX improvements
- [ ] Accessibility review

### Phase 4: Optimize
- [ ] Performance testing
- [ ] Bundle size analysis
- [ ] Dark mode testing
- [ ] Cross-browser testing

---

## 🔧 LOCAL DEVELOPMENT SETUP

```bash
# Backend (must be running)
cd backend
python -m uvicorn main:app --reload  # Runs on :8000

# Frontend
cd v2/frontend
npm install
npm run dev  # Runs on :5173

# Base URLs
Backend API: http://localhost:8000
Frontend App: http://localhost:5173
WebSocket: ws://localhost:8000/ws/logs
```

---

## 📚 FILE STRUCTURE SUMMARY

```
frontend/
  ├── login.html          (4.2 KB)
  ├── signup.html         (3.8 KB)
  ├── index.html          (6.5 KB)
  ├── project.html        (60 KB) - Workflow editor
  ├── style.css           (56.8 KB) - Green theme
  └── script.js           (referenced, not provided)

v2/frontend/src/
  ├── pages/
  │   ├── Login.tsx       (2.1 KB)
  │   ├── Signup.tsx      (2.3 KB)
  │   ├── Dashboard.tsx   (4.5 KB)
  │   └── Project.tsx     (7.4 KB)
  ├── nodes/
  │   └── BaseNode.tsx    (custom node component)
  ├── store/              (Zustand store)
  ├── lib/
  │   └── utils.ts        (cn utility)
  ├── index.css           (3.2 KB - Tailwind theme)
  └── App.tsx             (routing setup)
```

---

## 💡 IMPORTANT NOTES

1. **API_BASE_URL**: Currently hardcoded to `http://localhost:8000` in React
   - Should use environment variable: `VITE_API_BASE_URL`
   - Add `.env` file to v2/frontend

2. **Token Storage**: Using localStorage (not secure for sensitive data)
   - Consider: HttpOnly cookies after login
   - Implement: CSRF tokens if using cookies

3. **Error Handling**: Assumes backend returns `{ detail: "..." }` format
   - Verify: Backend error response structure

4. **WebSocket**: Needs testing for connection failures
   - Add: Retry logic and reconnection handling

5. **TypeScript**: React uses TypeScript, improve type safety
   - Add: Proper types for API responses
   - Add: Error type definitions

---

## 📞 NEXT STEPS

1. Read the full MIGRATION_ANALYSIS.md for comprehensive details
2. Review COLOR_SCHEME_REFERENCE.md for design decisions
3. Study FORMS_API_REFERENCE.md for validation patterns
4. Check migration_data.json for quick statistics
5. Start implementation with Phase 1 tasks

---

## 🎯 SUCCESS CRITERIA

✅ All legacy forms working in React
✅ Same API endpoints being called
✅ Same data being stored/retrieved
✅ Visual design maintaining brand consistency
✅ Performance improvements (85% size reduction)
✅ No feature loss (except intentional removals like email)
✅ All tests passing
✅ Responsive on all device sizes
