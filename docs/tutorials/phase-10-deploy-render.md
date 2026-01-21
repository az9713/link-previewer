# Phase 10: Deploy Backend to Render - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- How Platform-as-a-Service (PaaS) works
- How to deploy a Python/FastAPI backend to Render
- How to configure environment variables in production
- How to read deployment logs
- How free tier limitations affect your app

---

## 1. What Is Render?

### Platform Overview

Render is a cloud platform that makes deploying web applications simple:

```
Your Code (GitHub) → Render → Live URL
```

**Key features:**
- **Free tier** - Great for learning and small projects
- **Auto-deploy** - Pushes to GitHub trigger deployments
- **Managed infrastructure** - No server configuration needed
- **Built-in HTTPS** - Secure connections automatically

### Free Tier Limitations

**Important to understand:**

| Feature | Free Tier |
|---------|-----------|
| Web services | 750 hours/month |
| Sleep after inactivity | 15 minutes |
| Cold start time | ~50 seconds |
| RAM | 512 MB |
| Bandwidth | 100 GB/month |

**What "sleep after inactivity" means:**
- If no requests for 15 minutes, your service goes to sleep
- First request after sleep takes ~50 seconds (cold start)
- Subsequent requests are fast (~200ms)
- This is normal behavior, not an error

---

## 2. Prerequisites

Before starting, ensure you have:

- [ ] GitHub account with your code pushed
- [ ] Repository contains `backend/` directory
- [ ] `backend/requirements.txt` exists
- [ ] `backend/app/main.py` exists
- [ ] Local testing passes (backend works on localhost)

### Your Repository Structure

```
your-repo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── unfurl.py
│   └── requirements.txt
├── frontend/
│   └── ...
└── README.md
```

---

## 3. Step-by-Step Deployment

### Step 1: Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"** (recommended)
4. Authorize Render to access your GitHub account
5. Complete account setup

### Step 2: Create New Web Service

1. From the Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"** from the dropdown

### Step 3: Connect Your GitHub Account

1. On the "Create a new Web Service" page, you'll see options to connect a Git provider
2. Click the **"GitHub"** button under "Connect a repository"
3. A popup will appear asking to install Render on your GitHub account
4. **Choose "Only select repositories"** (recommended for security)
5. Select your `link-previewer` repository from the dropdown
6. Click **"Install"**

**GitHub 2FA Note:**
- If you have GitHub Mobile 2FA enabled, you may need to enter a one-time code on your phone
- After authentication, you'll be redirected back to Render

### Step 4: Select Your Repository

1. After GitHub is connected, you'll see your repositories listed
2. Find `link-previewer` in the list
3. Click **"Connect"** next to it

### Step 5: Configure the Service

Fill in the configuration form:

| Setting | Value | Explanation |
|---------|-------|-------------|
| **Name** | `link-previewer` | Your service name (appears in URL) |
| **Region** | Oregon (US West) | Choose closest to your users |
| **Branch** | `main` | Branch to deploy from |
| **Root Directory** | `backend` | Where your Python code lives |
| **Runtime** | Python 3 | Auto-detected usually |
| **Build Command** | `pip install -r requirements.txt` | Installs dependencies |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Starts FastAPI |

**Critical Settings Explained:**

**Root Directory: `backend`**
- Render will `cd backend` before running commands
- All paths are relative to this directory
- `requirements.txt` is found at `backend/requirements.txt`

**Start Command breakdown:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- `uvicorn` - ASGI server
- `app.main:app` - Import path (`app/main.py`, variable `app`)
- `--host 0.0.0.0` - Accept connections from anywhere
- `--port $PORT` - Use Render's assigned port (required!)

**Important UI Notes:**
- The Root Directory field shows a placeholder "e.g. src" - you need to click in the field and type `backend`
- The Build Command usually auto-populates correctly
- The Start Command may need to be entered manually - make sure to include the full command

### Step 6: Select Instance Type

1. Scroll down to **"Instance Type"** section
2. **Important:** The default selection may be **Starter ($7/month)** - you need to change this!
3. Click on **"Free"** to select it
4. The Free tier will show a purple/blue border when selected
5. You'll see the limitations: 750 hours/month, spins down after 15 min inactivity

### Step 7: Deploy

1. Click **"Create Web Service"** button
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Watch the build logs in real-time

### Step 8: Monitor Deployment

**Build logs show:**
```
==> Cloning from https://github.com/yourusername/link-previewer
==> Checking out commit abc1234
==> Using Python version: 3.11.0
==> Running build command 'pip install -r requirements.txt'
Collecting fastapi
Collecting uvicorn
...
==> Build successful
==> Starting service with 'uvicorn app.main:app --host 0.0.0.0 --port 10000'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

**Deployment takes 2-5 minutes** for the first build.

### Step 9: Get Your URL

Once deployed, your URL appears at the top:
```
https://your-service-name.onrender.com
```

Example: `https://link-previewer-ehwf.onrender.com`

---

## 4. Verify Deployment

### Test Health Endpoint

Open in browser or use curl:

```bash
curl https://your-service-name.onrender.com/health
```

**Expected response:**
```json
{"status": "healthy"}
```

**If you get a timeout or slow response:**
- This is the cold start (~50 seconds)
- Wait and try again - subsequent requests are fast

### Test API Documentation

Open in browser:
```
https://your-service-name.onrender.com/docs
```

You should see the Swagger UI with:
- POST `/unfurl` endpoint
- GET `/health` endpoint
- GET `/` root endpoint

### Test the Unfurl Endpoint

```bash
curl -X POST https://your-service-name.onrender.com/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "url": "https://github.com",
    "title": "GitHub: Let's build from here",
    "description": "GitHub is where over 100 million developers...",
    "image": "https://github.githubassets.com/...",
    "site_name": "GitHub"
  }
}
```

---

## 5. Environment Variables

### Why Environment Variables?

Environment variables store configuration that:
- Differs between environments (dev vs prod)
- Contains sensitive data (API keys, secrets)
- Shouldn't be committed to code

### Adding Environment Variables on Render

1. Go to your service dashboard
2. Click **"Environment"** in the left sidebar
3. Click **"Add Environment Variable"**
4. Enter:
   - **Key**: Variable name (e.g., `ALLOWED_ORIGINS`)
   - **Value**: Variable value
5. Click **"Save Changes"**

**Important:** After saving, Render automatically redeploys your service.

### Required Environment Variable: ALLOWED_ORIGINS

This is critical for CORS (Cross-Origin Resource Sharing).

**After you deploy your frontend to Vercel**, come back and add:

| Key | Value |
|-----|-------|
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app,http://localhost:5173,http://localhost:3000` |

Replace `your-app.vercel.app` with your actual Vercel URL.

**Why this matters:**
- Browsers block requests from different origins by default
- CORS headers tell browsers which origins are allowed
- Without this, your frontend cannot call your backend

---

## 6. Viewing Logs

### Access Logs

1. Go to your service dashboard
2. Click **"Logs"** in the left sidebar

### Log Types

**Build logs:** Show dependency installation and startup
**Runtime logs:** Show incoming requests and errors

**Example runtime logs:**
```
INFO:     127.0.0.1:54321 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54322 - "POST /unfurl HTTP/1.1" 200 OK
ERROR:    Failed to fetch https://invalid.url: Connection refused
```

### Debugging with Logs

If something goes wrong:
1. Check the logs for error messages
2. Look for Python tracebacks
3. Check if dependencies installed correctly
4. Verify the start command is correct

---

## 7. Auto-Deploy from GitHub

### How It Works

By default, Render watches your GitHub repository:
1. You push code to `main` branch
2. Render detects the change
3. Render automatically rebuilds and redeploys

### Viewing Deployment History

1. Go to your service dashboard
2. Click **"Events"** in the left sidebar
3. See all past deployments with status

### Manual Deploy

If you need to deploy without pushing code:
1. Click **"Manual Deploy"** dropdown
2. Select **"Deploy latest commit"**

---

## 8. Common Issues and Solutions

### Issue: Build Fails with "Module not found"

**Symptom:** Logs show `ModuleNotFoundError: No module named 'xyz'`

**Cause:** Missing dependency in requirements.txt

**Solution:**
1. Add the missing package to `requirements.txt`
2. Push to GitHub
3. Render will auto-redeploy

### Issue: Service Sleeping / Cold Start

**Symptom:** First request times out or takes 50+ seconds

**Cause:** Free tier services sleep after 15 minutes of inactivity

**Solution:** This is expected behavior. Options:
- Wait for cold start to complete
- Upgrade to paid tier for always-on service
- Use a service like UptimeRobot to ping your `/health` endpoint every 14 minutes (keeps it awake)

### Issue: Port Already in Use

**Symptom:** `Address already in use` error

**Cause:** Hardcoded port number instead of using `$PORT`

**Solution:** Ensure start command uses `--port $PORT`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue: 503 Service Unavailable

**Symptom:** Requests return 503 status code

**Causes:**
1. Service is sleeping (cold start)
2. Service crashed
3. Start command is wrong

**Solution:**
1. Check the logs for errors
2. Wait for cold start if no errors
3. Verify start command is correct

---

## 9. Quick Reference

### Your Deployment Settings

| Setting | Value |
|---------|-------|
| Platform | Render.com |
| Service Type | Web Service |
| Instance Type | Free |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Important URLs

| URL | Purpose |
|-----|---------|
| `https://your-service.onrender.com` | API base URL |
| `https://your-service.onrender.com/health` | Health check |
| `https://your-service.onrender.com/docs` | API documentation |

### Environment Variables to Add Later

| Variable | When to Add | Value |
|----------|-------------|-------|
| `ALLOWED_ORIGINS` | After frontend deployment | Your Vercel URL + localhost URLs |

---

## 10. Checklist

### Deployment Complete?

- [ ] Render account created
- [ ] Web service created and connected to GitHub
- [ ] Root directory set to `backend`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Deployment succeeded (green status)
- [ ] `/health` returns `{"status": "healthy"}`
- [ ] `/docs` shows Swagger UI
- [ ] `/unfurl` works with test URL

### Save Your URL

```
Backend URL: https://________________________.onrender.com
```

---

## Next Phase

Proceed to **Phase 11: Deploy Frontend to Vercel** to complete your deployment.

**Remember:** After deploying your frontend, return here to add the `ALLOWED_ORIGINS` environment variable!
