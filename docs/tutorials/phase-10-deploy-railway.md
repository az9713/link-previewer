# Phase 10: Deploy Backend to Railway - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- What Platform-as-a-Service (PaaS) is
- How Railway works as a deployment platform
- How CI/CD pipelines automate deployments
- How to deploy a Python/FastAPI application
- How to configure environment variables in production
- How to read and interpret deployment logs
- How to troubleshoot common deployment issues

---

## 1. Understanding Platform-as-a-Service (PaaS)

### What Is PaaS?

PaaS is a cloud computing model where the platform manages servers, and you just provide code:

```
Traditional Hosting          Platform-as-a-Service
┌────────────────────┐       ┌────────────────────┐
│ You manage:        │       │ Platform manages:  │
│ - Physical servers │       │ - Physical servers │
│ - Operating system │       │ - Operating system │
│ - Runtime (Python) │       │ - Runtime (Python) │
│ - Dependencies     │       │ - Dependencies     │
│ - Your code        │       │                    │
└────────────────────┘       │ You manage:        │
                             │ - Your code        │
                             │ - Environment vars │
                             └────────────────────┘
```

### Why Railway?

Railway is a modern PaaS that's:
- **Free tier available** - Great for learning and small projects
- **GitHub integration** - Auto-deploys when you push code
- **Automatic detection** - Detects Python from `requirements.txt`
- **Simple UI** - Easy to configure
- **Fast** - Deployments typically complete in 1-2 minutes

### Alternatives to Railway

| Platform | Pros | Cons |
|----------|------|------|
| **Railway** | Easy, free tier, fast deploys | Limited free hours |
| **Render** | Generous free tier | Slower deploys |
| **Fly.io** | Global deployment | More complex |
| **Heroku** | Pioneer of PaaS | Free tier removed |
| **DigitalOcean** | App Platform + VMs | Can get expensive |

---

## 2. Prerequisites

Before you begin, ensure you have:

- [ ] A GitHub account (https://github.com)
- [ ] Your code pushed to a GitHub repository
- [ ] A Railway account (we'll create this)

### Pushing Code to GitHub

If you haven't pushed your code yet:

**1. Create a new repository on GitHub:**
- Go to https://github.com/new
- Name it `link-previewer` (or your preferred name)
- Don't initialize with README (we already have code)
- Click "Create repository"

**2. Push your local code:**

```bash
# In your project root directory
cd C:\Users\yourname\path\to\deploy_brainstorm

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/link-previewer.git

# Create initial commit
git add .
git commit -m "Initial commit: Link Previewer service"

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 3. Creating a Railway Account

### Step 1: Sign Up

1. Go to https://railway.app
2. Click "Start a New Project" or "Login"
3. Choose "Login with GitHub" (recommended)
4. Authorize Railway to access your GitHub account

### Step 2: Verify Account

Railway may require:
- Email verification
- GitHub verification
- Credit card (for usage beyond free tier - you won't be charged if you stay in limits)

### Understanding Railway's Free Tier

As of 2024:
- **$5 free credit per month** (enough for small projects)
- **512 MB RAM** per service
- **1 GB disk**
- Services **sleep after inactivity** (spin up on first request)

---

## 4. Deploying the Backend

### Step 1: Create a New Project

1. From Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If prompted, **"Configure GitHub App"** to give Railway repo access
4. Select your **link-previewer repository**

### Step 2: Configure the Service

Railway will auto-detect Python from `requirements.txt`. You'll see:

```
Detected: Python
Builder: Nixpacks
```

**Important:** Railway needs to know which folder contains the backend.

1. Click on the service in the dashboard
2. Go to **Settings**
3. Under **Source**, find **Root Directory**
4. Set it to: `backend`

### Step 3: Set Environment Variables

1. Go to the **Variables** tab
2. Click **"New Variable"**
3. Add:

| Variable | Value |
|----------|-------|
| `ALLOWED_ORIGINS` | `http://localhost:5173` |
| `PORT` | (Railway sets this automatically) |

**Note:** We'll update `ALLOWED_ORIGINS` after deploying the frontend.

### Step 4: Deploy

Railway automatically deploys when you:
- Connect the repo (first deploy)
- Push new commits to the branch
- Click "Deploy" manually

Watch the **Deployment Logs** tab to see progress.

---

## 5. Understanding Deployment Logs

### The Build Phase

```
==============
Installing dependencies
==============
Collecting fastapi>=0.115.0
  Downloading fastapi-0.115.0-py3-none-any.whl (94 kB)
Collecting uvicorn[standard]>=0.32.0
  Downloading uvicorn-0.32.0-py3-none-any.whl (63 kB)
...
Successfully installed beautifulsoup4-4.12.3 fastapi-0.115.0 ...
```

This shows Railway:
1. Detecting Python
2. Reading `requirements.txt`
3. Installing dependencies

### The Run Phase

```
==============
Starting application
==============
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:PORT (Press CTRL+C to quit)
```

This shows:
1. Procfile/railway.json command being executed
2. Uvicorn starting
3. Application ready to receive requests

### Common Log Messages

| Message | Meaning |
|---------|---------|
| `Application startup complete` | Success! App is running |
| `ModuleNotFoundError` | Missing dependency in requirements.txt |
| `SyntaxError` | Python syntax error in your code |
| `Address already in use` | Port conflict (shouldn't happen on Railway) |
| `SIGTERM` | Railway stopping your app (sleep/redeploy) |

---

## 6. Getting Your API URL

### Finding the URL

1. In Railway dashboard, click on your service
2. Go to **Settings** tab
3. Under **Domains**, click **"Generate Domain"**
4. Railway creates: `your-app-name.up.railway.app`

### Testing the Deployment

**Test health endpoint:**
```bash
curl https://your-app-name.up.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

**Test the API:**
```bash
curl -X POST https://your-app-name.up.railway.app/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

**Test Swagger UI:**
Open in browser: `https://your-app-name.up.railway.app/docs`

---

## 7. CI/CD: Continuous Integration/Deployment

### What Is CI/CD?

```
You push code to GitHub
        ↓
GitHub notifies Railway
        ↓
Railway pulls code
        ↓
Railway builds app
        ↓
Railway deploys app
        ↓
App is live with new code!
```

All of this happens **automatically** every time you push.

### The Workflow

```
1. You: git push origin main
2. GitHub: Webhook → "New code pushed!"
3. Railway: "Got it, starting build..."
4. Railway: Installs dependencies
5. Railway: Runs start command
6. Railway: Health check passes
7. Railway: Routes traffic to new version
8. Old version is stopped
```

### Zero-Downtime Deployments

Railway (and most modern PaaS):
1. Starts the **new** version
2. Waits for health check to pass
3. Routes traffic to new version
4. Stops the old version

Your users never see downtime.

### Rolling Back

If something goes wrong:
1. Go to **Deployments** tab
2. Find a previous working deployment
3. Click **"Redeploy"**

Railway keeps deployment history.

---

## 8. Environment Variables in Production

### Why Not .env Files?

```
.env file = Local development only
Platform UI = Production

Why?
- .env files are in your code (bad for secrets)
- Platform encrypts variables
- Variables can differ per environment
- Team members don't need production secrets
```

### Setting Variables in Railway

1. **Service** → **Variables** tab
2. Click **"New Variable"**
3. Enter key and value
4. Click **"Add"**
5. Railway **automatically redeploys** with new variables

### Variable Scoping

Railway supports:
- **Service variables** - Only this service
- **Project variables** - Shared across services
- **Reference variables** - Link to other services (e.g., database URL)

For our app, service variables are sufficient.

---

## 9. Troubleshooting Common Issues

### Issue: "Build failed"

**Symptoms:**
- Build logs show errors
- Deployment never completes

**Common causes:**

1. **Missing dependency:**
   ```
   ModuleNotFoundError: No module named 'httpx'
   ```
   **Fix:** Add to requirements.txt

2. **Wrong Python version:**
   ```
   SyntaxError: invalid syntax
   ```
   **Fix:** Add `python-version` to railway.json or use nixpacks config

3. **Wrong root directory:**
   **Fix:** Set Root Directory to `backend` in Settings

### Issue: "Application error" (503)

**Symptoms:**
- App builds but won't start
- Browser shows 503 error

**Common causes:**

1. **Wrong start command:**
   **Fix:** Check Procfile matches your app structure

2. **Port not using $PORT:**
   **Fix:** Ensure `--port $PORT` in Procfile

3. **Import error on startup:**
   Check logs for Python import errors

### Issue: "Health check failed"

**Symptoms:**
- Build succeeds
- App starts but fails health check
- Railway keeps restarting

**Common causes:**

1. **No /health endpoint:**
   **Fix:** Add health endpoint to your app

2. **Health endpoint returns error:**
   **Fix:** Ensure `/health` returns 200 OK

3. **App takes too long to start:**
   **Fix:** Increase `healthcheckTimeout` in railway.json

### Issue: CORS errors from frontend

**Symptoms:**
- API works in browser/curl
- Frontend gets CORS errors

**Cause:** Frontend domain not in `ALLOWED_ORIGINS`

**Fix:**
1. Go to Variables
2. Update `ALLOWED_ORIGINS` to include frontend URL
3. Railway auto-redeploys

---

## 10. Monitoring Your Deployment

### Viewing Logs

1. Click on your service
2. Go to **Deployments** tab
3. Click on a deployment to see logs
4. Use **"View Logs"** for live logs

### Log Filtering

Railway logs show:
- Build logs (during deployment)
- Runtime logs (while running)
- HTTP request logs

You can filter by time, level, or search for text.

### Metrics

Railway provides basic metrics:
- CPU usage
- Memory usage
- Network traffic

For simple apps, these help identify:
- Memory leaks (RAM keeps growing)
- High CPU (inefficient code or high traffic)

---

## 11. Cost Management

### Monitoring Usage

1. Go to **Project Settings**
2. View **Usage** tab
3. See breakdown of:
   - Compute hours
   - Memory usage
   - Network egress

### Staying in Free Tier

Tips:
- Use one service (not multiple microservices)
- Let services sleep when not in use
- Don't run databases on Railway (use external free tier)
- Monitor usage weekly

### Sleep/Wake Behavior

Free tier services sleep after inactivity:
- First request may take 5-10 seconds (cold start)
- Subsequent requests are fast
- This is normal for free tier

---

## 12. Deployment Checklist

### Before Deployment

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` has all dependencies
- [ ] `Procfile` has correct start command
- [ ] `railway.json` (optional) has health check config
- [ ] `/health` endpoint exists and returns 200

### During Deployment

- [ ] Root directory set to `backend`
- [ ] Environment variables configured
- [ ] Domain generated
- [ ] Build logs show no errors
- [ ] Runtime logs show "Application startup complete"

### After Deployment

- [ ] `/health` endpoint responds
- [ ] `/docs` (Swagger) loads
- [ ] `/unfurl` endpoint works
- [ ] Note down your Railway URL for next phase

---

## 13. What We Deployed

### Files Railway Uses

```
backend/
├── Procfile              ← How to start the app
├── railway.json          ← Railway-specific config
├── requirements.txt      ← Python dependencies
└── app/
    ├── __init__.py
    ├── main.py           ← FastAPI application
    ├── models.py         ← Data models
    └── unfurl.py         ← URL extraction logic
```

### What Happens Behind the Scenes

1. **Nixpacks** detects Python from requirements.txt
2. Creates a container with Python runtime
3. Runs `pip install -r requirements.txt`
4. Executes command from Procfile
5. Routes HTTPS traffic to your app
6. Monitors health endpoint

---

## 14. Self-Check Questions

1. **What is PaaS and how does it differ from traditional hosting?**

   Answer: PaaS manages infrastructure (servers, OS, runtime). You only provide code and configuration. Traditional hosting requires you to manage everything.

2. **Why do we set Root Directory to 'backend'?**

   Answer: Our repository has both frontend and backend. Railway needs to know which folder contains the Python app to build and deploy.

3. **What does CI/CD mean and how does Railway implement it?**

   Answer: CI/CD is Continuous Integration/Deployment. Railway auto-deploys when you push to GitHub - it pulls code, builds, and deploys without manual intervention.

4. **Why don't we use .env files in production?**

   Answer: .env files would be in your code/repo, which isn't secure for secrets. Production platforms provide encrypted variable storage through their UI.

5. **What happens if a deployment fails the health check?**

   Answer: Railway keeps the old version running and marks the new deployment as failed. Your users never see the broken version.

6. **How do you roll back a broken deployment?**

   Answer: Go to Deployments tab, find a previous working deployment, click Redeploy.

7. **Why does the first request after inactivity take longer?**

   Answer: Free tier services sleep when inactive. First request wakes them up (cold start). This saves resources but adds latency.

8. **What should you check if you see CORS errors after deployment?**

   Answer: Ensure your frontend's domain is in the `ALLOWED_ORIGINS` environment variable and redeploy.

---

## Next Phase

With the backend deployed, we'll deploy the frontend to Vercel in **Phase 11: Deploy Frontend to Vercel**.

Remember to **save your Railway URL** - you'll need it to configure the frontend!

Example: `https://link-previewer-backend.up.railway.app`

