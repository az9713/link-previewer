# Phase 9: Deployment Preparation - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- What deployment preparation means
- Why secrets shouldn't be in code
- How environment variables work
- What a Procfile is and why platforms need it
- Difference between development and production builds
- The 12-Factor App methodology
- How to configure different environments

---

## 1. Why Deployment Preparation?

### The Problem

Your app works perfectly on your computer. But to put it on the internet:

```
Your Computer                    The Cloud
┌─────────────────┐              ┌─────────────────┐
│ - Has your code │              │ - Has your code │
│ - Port 8000     │      →       │ - Port ???      │
│ - localhost     │              │ - random URL    │
│ - Your settings │              │ - Their settings│
└─────────────────┘              └─────────────────┘
```

**Challenges:**
1. **Port numbers:** Cloud platforms assign random ports
2. **URLs:** Your frontend URL isn't known until deployed
3. **Secrets:** API keys shouldn't be in code (someone might see them)
4. **Startup:** The platform needs to know how to run your app

### The Solution: Configuration

Make your app **configurable** so it adapts to any environment:

```python
# Bad: Hardcoded values
PORT = 8000
ALLOWED_ORIGINS = ["http://localhost:5173"]

# Good: Read from environment
PORT = os.environ.get("PORT", 8000)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
```

---

## 2. Environment Variables Explained

### What Are Environment Variables?

Environment variables are **key-value pairs** set outside your code:

```bash
# Setting environment variables
export DATABASE_URL="postgres://user:pass@host/db"
export API_KEY="sk_live_12345"
export PORT="8000"
```

Your code reads them:

```python
import os

database_url = os.environ.get("DATABASE_URL")
api_key = os.environ.get("API_KEY")
port = int(os.environ.get("PORT", 8000))  # 8000 is the default
```

### Why Use Environment Variables?

**1. Security - Keep Secrets Out of Code**

```python
# NEVER DO THIS - secrets in code
API_KEY = "sk_live_12345"  # Anyone who sees your code sees this!

# DO THIS - secrets in environment
API_KEY = os.environ.get("API_KEY")  # Code is safe to share
```

If you commit secrets to Git:
- They're in the history forever
- Anyone with repo access can see them
- Bots scan GitHub for leaked keys
- Your accounts can be compromised

**2. Flexibility - Different Values Per Environment**

```
Development:
  DATABASE_URL = "sqlite:///./test.db"
  DEBUG = "true"

Production:
  DATABASE_URL = "postgres://prod-server/db"
  DEBUG = "false"
```

Same code, different behavior based on where it runs.

**3. Portability - Works on Any Platform**

Environment variables work everywhere:
- Your laptop
- Docker containers
- Railway, Vercel, AWS
- Kubernetes
- GitHub Actions

### How to Set Environment Variables

**On Your Computer (Windows):**

```cmd
:: Temporary (current terminal only)
set PORT=8000

:: Permanent (requires restart)
setx PORT "8000"
```

**On Your Computer (Mac/Linux):**

```bash
# Temporary (current terminal only)
export PORT=8000

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PORT=8000' >> ~/.bashrc
```

**In a .env File:**

```bash
# .env file
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173
```

Note: `.env` files are for **local development only**. They should be in `.gitignore`.

**On Deployment Platforms:**

Railway, Vercel, and others have a UI to set environment variables. This is the secure way to handle secrets in production.

### Reading Environment Variables in Python

```python
import os

# Basic - returns None if not set
value = os.environ.get("MY_VAR")

# With default value
value = os.environ.get("MY_VAR", "default_value")

# Required - raises error if not set
value = os.environ["MY_VAR"]  # KeyError if missing

# Type conversion
port = int(os.environ.get("PORT", 8000))
debug = os.environ.get("DEBUG", "false").lower() == "true"

# List from comma-separated string
origins = os.environ.get("ALLOWED_ORIGINS", "").split(",")
```

### Reading Environment Variables in JavaScript (Vite)

Vite handles environment variables specially:

```javascript
// Only variables starting with VITE_ are exposed
const apiUrl = import.meta.env.VITE_API_URL;

// Built-in variables
const mode = import.meta.env.MODE;        // 'development' or 'production'
const isDev = import.meta.env.DEV;        // true in development
const isProd = import.meta.env.PROD;      // true in production
```

**Important:** Vite embeds these at **build time**, not runtime. If you change an environment variable, you must rebuild.

---

## 3. The Procfile Explained

### What Is a Procfile?

A Procfile tells the deployment platform how to start your application:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Breakdown:**

| Part | Meaning |
|------|---------|
| `web:` | Process type (web server that receives HTTP requests) |
| `uvicorn` | The command to run |
| `app.main:app` | Python module path to your FastAPI app |
| `--host 0.0.0.0` | Listen on all network interfaces |
| `--port $PORT` | Use the port assigned by the platform |

### Why We Need It

Deployment platforms don't know:
- What language your app uses
- How to start it
- What the main file is

The Procfile answers: "Run this command to start the web server."

### Process Types

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: python worker.py
clock: python scheduler.py
```

| Type | Purpose |
|------|---------|
| `web` | Receives HTTP requests |
| `worker` | Background job processing |
| `clock` | Scheduled tasks (cron jobs) |

Most simple apps only need `web`.

### Host and Port Explained

**Why `--host 0.0.0.0`?**

```
--host 127.0.0.1    → Only accessible from the same machine
--host 0.0.0.0      → Accessible from any network interface
```

In development, `127.0.0.1` (localhost) is fine.
In production, the platform routes traffic to your app, so it needs to listen on all interfaces.

**Why `$PORT`?**

Cloud platforms assign ports dynamically:

```
Your app might get:
  - Port 3000 on one deploy
  - Port 5432 on another
  - Port 8080 somewhere else
```

The platform sets the `PORT` environment variable, and your app reads it:

```python
port = int(os.environ.get("PORT", 8000))
```

### Railway-Specific Configuration

Railway supports a `railway.json` file for additional configuration:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

| Option | Purpose |
|--------|---------|
| `builder` | How to build (NIXPACKS auto-detects Python) |
| `startCommand` | Same as Procfile |
| `healthcheckPath` | Endpoint to verify app is healthy |
| `restartPolicyType` | Restart if it crashes |

---

## 4. CORS in Production

### The CORS Problem (Revisited)

In production:

```
Frontend: https://my-app.vercel.app
Backend:  https://my-api.up.railway.app

Different domains = CORS applies!
```

The browser blocks requests unless the backend explicitly allows the frontend's domain.

### Our CORS Configuration

```python
# In main.py
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**In Development:**
- Default origins: `localhost:5173`, `localhost:3000`
- No environment variable needed

**In Production:**
- Set `ALLOWED_ORIGINS` to include your Vercel URL
- Example: `ALLOWED_ORIGINS=https://my-app.vercel.app,http://localhost:5173`

### Common CORS Mistakes

**1. Forgetting to Add Production URL**

```python
# Backend allows localhost only
ALLOWED_ORIGINS = ["http://localhost:5173"]

# Frontend at https://my-app.vercel.app
# Result: CORS error! Browser blocks the request
```

**2. Using Wildcard in Production**

```python
# Allows any website to call your API
allow_origins=["*"]  # Dangerous in production!
```

This means any website can call your API. For a public API that's okay, but for private APIs it's a security risk.

**3. Not Redeploying After Change**

If you add a new origin, you must redeploy the backend for it to take effect.

---

## 5. Production Builds

### Development vs Production

**Development Mode:**
- Source maps (for debugging)
- Unminified code (readable)
- Hot module replacement (instant updates)
- Development warnings
- Larger file sizes

**Production Mode:**
- Minified code (smaller)
- No source maps (or external)
- Optimized for performance
- No development warnings
- Tree-shaking (removes unused code)

### Building the Frontend for Production

```bash
cd frontend
npm run build
```

This creates a `dist/` folder:

```
frontend/
├── dist/
│   ├── index.html        # Entry point
│   ├── assets/
│   │   ├── index-abc123.js    # Minified JavaScript
│   │   └── index-def456.css   # Minified CSS
```

**File sizes comparison:**

| Mode | JavaScript | CSS |
|------|------------|-----|
| Development | ~500 KB | ~50 KB |
| Production | ~150 KB | ~15 KB |

### What Minification Does

```javascript
// Before (development)
function calculateTotalPrice(items, taxRate, discount) {
  const subtotal = items.reduce((sum, item) => {
    return sum + item.price * item.quantity;
  }, 0);
  const tax = subtotal * taxRate;
  const total = subtotal + tax - discount;
  return total;
}

// After (production)
function c(i,t,d){return i.reduce((s,e)=>s+e.price*e.quantity,0)*(1+t)-d}
```

Same functionality, much smaller file.

### Preview Production Build Locally

```bash
cd frontend
npm run build
npm run preview
```

This serves the production build locally so you can test it before deploying.

---

## 6. The 12-Factor App Methodology

The 12-Factor App is a set of best practices for building cloud-native applications. Here are the most relevant factors for our project:

### Factor III: Config (Store config in the environment)

```
✓ We do this:
  - ALLOWED_ORIGINS from environment
  - PORT from environment
  - VITE_API_URL from environment

✗ Anti-pattern:
  - Hardcoded URLs
  - Config files with secrets
```

### Factor IV: Backing Services (Treat backing services as attached resources)

```
✓ We do this:
  - API URL is configurable
  - Could easily swap to different backend

✗ Anti-pattern:
  - Hardcoded database connections
  - Tight coupling to specific services
```

### Factor V: Build, Release, Run (Strictly separate build and run stages)

```
Build Stage:  npm run build  → Creates dist/
Release Stage: Deploy dist/ + config to platform
Run Stage:    Platform serves the files
```

### Factor X: Dev/Prod Parity (Keep development, staging, and production as similar as possible)

```
✓ We do this:
  - Same code runs locally and in production
  - Same frameworks and tools
  - Only configuration differs

✗ Anti-pattern:
  - Using SQLite locally but Postgres in production
  - Different code paths for different environments
```

---

## 7. Environment-Specific Configuration

### The Pattern

```
.env.example     ← Template (committed to Git)
.env             ← Local values (NOT committed)
Platform UI      ← Production values
```

### Backend .env.example

```bash
# Backend Environment Variables
# Copy this file to .env and fill in your values

# Allowed origins for CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Port (Railway sets this automatically)
PORT=8000
```

### Frontend .env.example

```bash
# Frontend Environment Variables

# API URL - leave empty for local dev (uses Vite proxy)
# VITE_API_URL=/api

# For production, set to your Railway URL:
# VITE_API_URL=https://your-backend.up.railway.app
```

### Setting Up Local Environment

```bash
# Backend
cd backend
copy .env.example .env  # Windows
# or: cp .env.example .env  # Mac/Linux

# Frontend
cd frontend
copy .env.example .env  # Windows
# or: cp .env.example .env  # Mac/Linux
```

Then edit `.env` with your local values.

---

## 8. Files Created for Deployment

### Procfile (backend/Procfile)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

One line that tells Railway how to start the app.

### railway.json (backend/railway.json)

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

Railway-specific configuration with health checks.

### .env.example files

Templates for environment variables. Developers copy these to `.env` and fill in values.

---

## 9. Deployment Checklist

### Backend Ready for Deployment

- [x] `Procfile` created with correct start command
- [x] `railway.json` with health check configuration
- [x] CORS reads from `ALLOWED_ORIGINS` environment variable
- [x] Port reads from `PORT` environment variable
- [x] `/health` endpoint exists for health checks
- [x] `.env.example` documents required variables
- [x] No secrets hardcoded in code
- [x] `.gitignore` excludes `.env` files

### Frontend Ready for Deployment

- [x] API URL reads from `VITE_API_URL` environment variable
- [x] Fallback to `/api` for local development (Vite proxy)
- [x] `npm run build` produces working production build
- [x] `.env.example` documents required variables
- [x] No secrets hardcoded in code

---

## 10. Testing the Production Build

### Test Backend Production Mode

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux

# Set environment variables
set PORT=8000  # Windows
# or: export PORT=8000  # Mac/Linux

# Run without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port %PORT%  # Windows
# or: uvicorn app.main:app --host 0.0.0.0 --port $PORT  # Mac/Linux
```

### Test Frontend Production Build

```bash
cd frontend

# Build for production
npm run build

# Preview the build
npm run preview
```

The preview server runs on port 4173 by default.

### Test End-to-End

1. Run backend in production mode (port 8000)
2. Build frontend: `npm run build`
3. Preview frontend: `npm run preview`
4. Set `VITE_API_URL=http://localhost:8000` before building
5. Open `http://localhost:4173`
6. Test a URL preview

---

## 11. What Happens During Deployment

### Backend Deployment to Railway

```
1. You push to GitHub
2. Railway detects the push
3. Railway reads Procfile/railway.json
4. Railway detects Python (requirements.txt)
5. Railway creates a container
6. Railway installs dependencies (pip install)
7. Railway runs the start command
8. Railway assigns a URL (*.up.railway.app)
9. Railway monitors health endpoint
10. Your API is live!
```

### Frontend Deployment to Vercel

```
1. You push to GitHub
2. Vercel detects the push
3. Vercel detects Vite project
4. Vercel runs: npm install
5. Vercel runs: npm run build
6. Vercel takes the dist/ folder
7. Vercel deploys to CDN
8. Vercel assigns a URL (*.vercel.app)
9. Your frontend is live!
```

---

## 12. Self-Check Questions

1. **Why should secrets never be in your code?**

   Answer: Code is often shared (GitHub, colleagues). If secrets are in code, anyone with access can see them. Git history preserves them forever. Use environment variables instead.

2. **What does the Procfile do?**

   Answer: Tells the deployment platform how to start your application. It specifies the process type (`web`) and the command to run.

3. **Why do we use `$PORT` instead of a hardcoded port number?**

   Answer: Cloud platforms assign ports dynamically. They set the `PORT` environment variable, and our app reads it. This makes the app portable across platforms.

4. **What's the difference between development and production builds?**

   Answer: Development builds are larger, unminified, and include debugging tools. Production builds are minified, optimized, and smaller for faster loading.

5. **Why do we need to update CORS for production?**

   Answer: CORS is domain-based. In production, frontend and backend have different domains. The backend must explicitly allow the frontend's domain.

6. **What are the three stages of deployment according to 12-Factor?**

   Answer: Build (compile/package code), Release (combine build with config), Run (execute in the environment).

7. **Why isn't `.env` committed to Git?**

   Answer: `.env` may contain secrets. We commit `.env.example` as a template, and each developer/environment creates their own `.env`.

8. **What does `--host 0.0.0.0` mean?**

   Answer: Listen on all network interfaces, not just localhost. Required in production so the platform can route traffic to your app.

---

## Next Phase

Now that we've prepared for deployment, we'll actually deploy in **Phase 10: Deploy Backend to Railway**.

