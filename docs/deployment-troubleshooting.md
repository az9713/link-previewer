# Deployment Troubleshooting Guide

This guide documents common problems encountered during deployment and their solutions, based on real deployment experience.

---

## Quick Diagnosis Flowchart

```
"Failed to fetch" error
        │
        ▼
Is backend running?
   ├── Visit: https://your-backend.onrender.com/health
   │
   └── If timeout or 503 ──────────────────────────────┐
        │                                               │
        ▼                                               ▼
  Backend is sleeping                        Backend crashed
  (Render free tier)                         Check Render logs
        │
        ▼
  Wait ~50 seconds
  for cold start
        │
        ▼
Is CORS configured?
   ├── Check Render → Environment
   │   → ALLOWED_ORIGINS includes Vercel URL?
   │
   └── If missing ─────────────────────────────────────┐
        │                                               │
        ▼                                               ▼
  Add ALLOWED_ORIGINS                         Wait for Render
  with your Vercel URL                        to redeploy
        │
        ▼
Is VITE_API_URL correct?
   ├── Check Vercel → Settings → Environment Variables
   │
   └── If wrong or missing ────────────────────────────┐
        │                                               │
        ▼                                               ▼
  Fix the variable                            Redeploy on Vercel
  (must match Render URL)                     (build-time variable!)
```

---

## Problem 1: 503 Service Unavailable

### Symptoms
- Request returns 503 status code
- "Service Unavailable" message
- Network tab shows 503

### Root Cause
**Render free tier spins down services after 15 minutes of inactivity.** When you make a request to a sleeping service, it needs to "cold start" (spin up), which takes ~50 seconds.

### This Is NOT a Bug or Broken Deployment!

**Important:** A 503 error or long loading time after the site has been idle is **completely normal** for Render's free tier. Your deployment is working correctly. The service is just "waking up."

**What happens:**
1. No requests for 15 minutes → Render stops your service to save resources
2. Next request arrives → Render restarts your service
3. ~50 seconds later → Service is running, request completes
4. Subsequent requests → Fast (~200ms) until next 15-min idle period

### Solution
1. **Wait for cold start:** The first request triggers the service to wake up
2. **Visit the health endpoint:** Open `https://your-backend.onrender.com/health`
3. **Wait ~50 seconds** for the service to start
4. **Retry your request**

### Prevention Options
- **Upgrade to paid tier:** Services stay always-on
- **Use an uptime monitor:** Services like UptimeRobot can ping your `/health` endpoint every 14 minutes to keep it awake (free tier available)

---

## Problem 2: CORS Policy Error

### Symptoms
- Browser console shows:
  ```
  Access to fetch at 'https://your-backend.onrender.com/unfurl' from origin
  'https://your-app.vercel.app' has been blocked by CORS policy
  ```
- Network tab shows failed OPTIONS (preflight) request
- Request never reaches the backend

### Root Cause
The backend's CORS configuration doesn't include your Vercel frontend URL. By default, the backend only allows:
```python
ALLOWED_ORIGINS = "http://localhost:5173,http://localhost:3000"
```

### Solution
1. Go to **https://dashboard.render.com**
2. Click on **"My project"** (or your project group name)
3. Click on your backend service (e.g., `link-previewer`)
4. Click **"Environment"** in the left sidebar
5. Click the **"+ Add"** button
6. Select **"New variable"** from the dropdown
7. Add:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** `https://your-app.vercel.app,http://localhost:5173,http://localhost:3000`
8. Click **"Save, rebuild, and deploy"**
9. **Verify:** Click "Events" in sidebar and wait for "Deploy live" status

### Common Mistakes
| Mistake | Correct |
|---------|---------|
| `https://your-app.vercel.app/` (trailing slash) | `https://your-app.vercel.app` |
| `http://your-app.vercel.app` (http) | `https://your-app.vercel.app` (https) |
| `your-app.vercel.app` (missing protocol) | `https://your-app.vercel.app` |
| Spaces after commas | No spaces: `url1,url2,url3` |

---

## Problem 3: "Failed to fetch" Error

### Symptoms
- UI shows generic "Failed to fetch" error
- Network tab shows failed request
- No response data

### Possible Causes and Fixes

**Cause 1: Backend not running**
- Check: Visit `https://your-backend.onrender.com/health`
- Fix: Wait for cold start or check Render logs for errors

**Cause 2: CORS not configured**
- Check: Look for CORS error in browser console
- Fix: Add `ALLOWED_ORIGINS` environment variable on Render

**Cause 3: Wrong API URL**
- Check: Verify `VITE_API_URL` in Vercel → Settings → Environment Variables
- Fix: Correct the URL and **redeploy** (build-time variable)

**Cause 4: Network issues**
- Check: Can you reach the backend directly from browser?
- Fix: Try a different network or wait

---

## Problem 4: API URL is Undefined

### Symptoms
- Request goes to wrong URL (e.g., `undefined/unfurl`)
- Console shows undefined errors
- API calls fail with 404

### Root Cause
The `VITE_API_URL` environment variable is not set or misspelled on Vercel.

### Solution
1. Go to **Vercel → your project → Settings → Environment Variables**
2. Add or fix:
   - **Key:** `VITE_API_URL` (exact spelling, with underscores)
   - **Value:** `https://your-backend.onrender.com`
3. **Critical:** Click **"Redeploy"** after changing
   - Vite embeds environment variables at build time
   - Without redeployment, the old values remain

---

## Problem 5: Build Fails on Vercel

### Symptoms
- Deployment fails during build step
- Build logs show errors

### Common Errors and Fixes

**Error: "Module not found: Can't resolve 'react'"**
```
Fix: Ensure dependencies are in package.json, not just devDependencies
```

**Error: "Cannot find module './App'"** (case sensitivity)
```
Windows:  App.jsx and app.jsx are the same file
Linux:    App.jsx and app.jsx are DIFFERENT files

Fix: Match exact casing in imports
     import App from './App.jsx'  // Must match file exactly
```

**Error: "Build failed: exit code 1"**
```
Check build logs for:
- TypeScript errors
- ESLint errors
- Syntax errors
- Missing dependencies

Fix: Run `npm run build` locally first to catch errors
```

---

## Problem 6: Root Directory Issues

### Symptoms (Render)
- Build fails with "requirements.txt not found"
- Start command fails to find `app.main`

### Symptoms (Vercel)
- Build fails with "package.json not found"
- Wrong content deployed

### Root Cause
Root Directory not set correctly. This is a monorepo with separate `backend/` and `frontend/` directories.

### Solution
- **Render:** Set Root Directory to `backend`
- **Vercel:** Set Root Directory to `frontend`

---

## Problem 7: Wrong Port on Render

### Symptoms
- Backend starts but requests fail
- "Connection refused" errors

### Root Cause
Hardcoded port number instead of using `$PORT` environment variable.

### Solution
Use this Start Command on Render:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Don't use:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000  # Wrong!
```

Render assigns a dynamic port via `$PORT`.

---

## Problem 8: Environment Variables Not Taking Effect

### On Render (Runtime Variables)
- Changes take effect after auto-redeploy
- Check the "Events" tab to confirm deployment completed
- May take 1-2 minutes

### On Vercel (Build-time Variables)
- Changes require manual redeployment
- Go to Deployments → click "..." → "Redeploy"
- Select "Redeploy with existing Build Cache" or fresh build

---

## Problem 9: Preview Works Locally, Fails in Production

### Debugging Steps

1. **Compare environments:**
   | Setting | Local | Production |
   |---------|-------|------------|
   | Frontend URL | localhost:5173 | your-app.vercel.app |
   | Backend URL | localhost:8000 | your-backend.onrender.com |
   | CORS | localhost allowed | Production URL needed |

2. **Check DevTools Network tab:**
   - What URL is the request going to?
   - What status code is returned?
   - Are there CORS headers in the response?

3. **Test backend directly:**
   ```bash
   curl https://your-backend.onrender.com/health
   curl -X POST https://your-backend.onrender.com/unfurl \
     -H "Content-Type: application/json" \
     -d '{"url": "https://github.com"}'
   ```

---

## Verification Commands

### Test Backend Health
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status": "healthy"}
```

### Test Backend API
```bash
curl -X POST https://your-backend.onrender.com/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
# Expected: {"success": true, "data": {...}}
```

### Test CORS Preflight
```bash
curl -X OPTIONS https://your-backend.onrender.com/unfurl \
  -H "Origin: https://your-app.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
# Look for: Access-Control-Allow-Origin header
```

---

## Environment Variable Reference

### Render (Backend)

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://app.vercel.app,http://localhost:5173` |

### Vercel (Frontend)

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `VITE_API_URL` | Backend API URL | `https://backend.onrender.com` |

**Remember:**
- Render variables: Runtime (auto-redeploy)
- Vercel variables: Build-time (manual redeploy required)

---

## Problem 10: HTTP 429 Rate Limiting from Major Sites

### Symptoms
- Request returns 429 status code
- Error message: "HTTP error 429 while fetching [URL]"
- Happens consistently with certain sites (Yahoo, LinkedIn, etc.)
- Works fine with other sites (GitHub, Wikipedia)

### Root Cause
Some major websites actively block or rate-limit automated requests. This happens for several reasons:

**1. Bot User-Agent Detection**

Our backend identifies itself as a bot:
```python
USER_AGENT = (
    "Mozilla/5.0 (compatible; LinkPreviewer/1.0; "
    "+https://github.com/your-username/link-previewer)"
)
```

Sites like Yahoo see `LinkPreviewer/1.0` and immediately rate-limit or block.

**2. Cloud Provider IP Blocking**

Render's free tier uses shared IP addresses. These IPs:
- Are known to hosting providers
- May be flagged due to other users' abuse
- Are often preemptively blocked by protective sites

**3. Aggressive Bot Protection**

Many sites use services like Cloudflare, Akamai, or custom bot protection that:
- Analyze request patterns
- Check for browser fingerprints
- Block requests that look automated

### Sites That Commonly Block Preview Bots

| Site | Behavior | Reason |
|------|----------|--------|
| **Yahoo** | 429 rate limit | Aggressive bot protection |
| **LinkedIn** | 999 or 429 | Heavy anti-scraping measures |
| **Facebook** | Varies | Requires special tokens for some content |
| **Instagram** | 403 or 429 | Strict bot blocking |
| **Twitter/X** | Often blocked | API-focused, blocks scraping |
| **News sites with paywalls** | 403 | Protect premium content |
| **Banking/financial sites** | 403 | Security measures |

### This Is Expected Behavior

**Important:** This is NOT a bug in your code. These sites intentionally block preview services. Even major services like Slack, Discord, and iMessage face similar challenges and use special arrangements or workarounds.

### What You Can Do

**Option 1: Accept the limitation (Recommended)**

Display a user-friendly error message:
```
"This site doesn't allow link previews. Try opening the link directly."
```

**Option 2: Use different test URLs**

For testing and demos, use sites known to work well:
- `https://github.com`
- `https://wikipedia.org`
- `https://dev.to`
- `https://medium.com`
- `https://stackoverflow.com`

**Option 3: Add retry logic with delays**

For borderline cases, adding delays between retries might help:
```python
import asyncio

async def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = await fetch(url)
        if response.status_code != 429:
            return response
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return response
```

**Option 4: Paid proxy services (Advanced)**

For production applications needing high success rates:
- Residential proxy services rotate IPs
- Some services specialize in web scraping
- Significantly increases complexity and cost

### Solution Summary

| Approach | Effort | Reliability |
|----------|--------|-------------|
| Accept limitation | None | N/A - graceful failure |
| Use friendly sites for testing | Low | High for those sites |
| Retry with backoff | Medium | Slightly improved |
| Proxy services | High | Much improved |

For a learning project, accepting the limitation and using test-friendly URLs is the pragmatic choice.

---

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Vercel Documentation:** https://vercel.com/docs
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **Vite Documentation:** https://vitejs.dev

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| 503 Service Unavailable | Wait ~50s for cold start |
| CORS Error | Add Vercel URL to Render ALLOWED_ORIGINS |
| Failed to fetch | Check backend health, then CORS, then VITE_API_URL |
| Undefined API URL | Add VITE_API_URL on Vercel, then redeploy |
| Build fails | Check case sensitivity, run build locally first |
| Port issues | Use `--port $PORT` in Render start command |
| 429 Rate Limited | Expected for Yahoo, LinkedIn, etc. - use GitHub for testing |
