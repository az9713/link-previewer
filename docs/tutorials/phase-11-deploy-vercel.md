# Phase 11: Deploy Frontend to Vercel - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- How static site hosting differs from server hosting
- What Vercel is and how it works
- How CDNs make websites fast globally
- Build-time vs runtime environment variables
- How to deploy a React/Vite application
- How to configure the frontend to connect to the backend

---

## 1. Understanding Static Site Hosting

### What Is Static Site Hosting?

Static sites are pre-built HTML, CSS, and JavaScript files:

```
Build Phase (on Vercel):
┌─────────────────────────┐
│  React Components       │
│  + JSX + CSS            │──→ npm run build ──→ dist/
│  + JavaScript           │                       ├── index.html
└─────────────────────────┘                       ├── assets/
                                                  │   ├── index-abc.js
                                                  │   └── index-def.css
                                                  └── (static files)

Serve Phase:
┌──────────────┐          ┌─────────────────────────────┐
│   Browser    │ ──────→  │        CDN (Vercel)         │
│   Request    │          │                             │
└──────────────┘          │  Returns pre-built files    │
                          │  (no server processing)      │
                          └─────────────────────────────┘
```

### Static vs Dynamic Hosting

| Static (Vercel, Netlify) | Dynamic (Railway, Heroku) |
|--------------------------|---------------------------|
| Pre-built files | Code runs on every request |
| No server processing | Server processes requests |
| Extremely fast | Depends on code complexity |
| Cheap/free | Uses compute resources |
| Can't have secrets | Can securely use secrets |
| Perfect for React | Required for APIs |

### Why Vercel for Frontend?

Vercel is optimized for frontend frameworks:
- **Automatic framework detection** - Knows how to build Vite/React
- **Global CDN** - Files served from nearest location
- **HTTPS by default** - Secure connections
- **Generous free tier** - Plenty for personal projects
- **Preview deployments** - Every PR gets a URL

---

## 2. What Is a CDN?

### Content Delivery Network Explained

A CDN is a network of servers worldwide that cache and serve your content:

```
Without CDN:
User in Tokyo → ────────────────────→ Server in US → Response
                     (high latency)

With CDN:
User in Tokyo → → CDN Edge (Tokyo) → Response
                   (low latency)

CDN Edge Locations:
   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
   │Tokyo│  │London│  │NYC │  │Sydney│
   └─────┘  └─────┘  └─────┘  └─────┘
       ↑        ↑        ↑        ↑
       └────────┴────────┴────────┘
              All serve your files
```

### Why CDN Matters

| Metric | Without CDN | With CDN |
|--------|-------------|----------|
| Load time (nearby) | 200ms | 50ms |
| Load time (far) | 2000ms | 100ms |
| Reliability | One server | Many servers |
| DDoS protection | Vulnerable | Protected |

For static sites, CDNs provide:
- **Speed** - Files are close to users
- **Reliability** - If one edge fails, another serves
- **Scale** - Handle millions of requests
- **Cost** - Bandwidth is cheap on CDNs

---

## 3. Build-Time vs Runtime Variables

### The Critical Difference

**Runtime variables (Backend - Railway):**
- Read when code executes
- Can change without rebuilding
- Secrets are safe (never sent to browser)

**Build-time variables (Frontend - Vercel):**
- Embedded into JavaScript during build
- Changing requires rebuild
- Are visible in browser (not for secrets!)

### How Vite Handles Environment Variables

```javascript
// In your code
const apiUrl = import.meta.env.VITE_API_URL;

// During build:
// Vite literally replaces import.meta.env.VITE_API_URL
// with the actual value

// Becomes:
const apiUrl = "https://your-api.up.railway.app";
```

### Security Implications

```
VITE_API_URL=https://api.example.com     ✓ OK (public URL)
VITE_API_KEY=secret123                   ✗ NEVER (visible to anyone!)
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...  ✓ OK (publishable keys are meant to be public)
VITE_DATABASE_PASSWORD=secret            ✗ NEVER (secrets go in backend only)
```

**Rule:** Only put public information in frontend environment variables.

---

## 4. Prerequisites

Before deploying, ensure you have:

- [ ] GitHub account with your code pushed
- [ ] Backend deployed on Railway (from Phase 10)
- [ ] Your Railway API URL (e.g., `https://your-app.up.railway.app`)
- [ ] A Vercel account (we'll create this)

---

## 5. Creating a Vercel Account

### Step 1: Sign Up

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"** (recommended)
4. Authorize Vercel to access your GitHub

### Step 2: Understand Free Tier

Vercel's free tier includes:
- **100 GB bandwidth** per month
- **Unlimited** static sites
- **Serverless functions** (100 GB-hours)
- **Automatic HTTPS**
- **Preview deployments** for PRs

More than enough for learning and small projects.

---

## 6. Deploying the Frontend

### Step 1: Import Project

1. From Vercel dashboard, click **"Add New..."** → **"Project"**
2. Click **"Import"** next to your GitHub repository
3. Vercel detects it's a Vite project

### Step 2: Configure Project

Vercel shows you configuration options:

**Framework Preset:** `Vite` (auto-detected)

**Root Directory:** Click **"Edit"** and select `frontend`

**Build Settings:**
```
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

(These are usually auto-detected correctly)

### Step 3: Set Environment Variables

Click **"Environment Variables"** to add:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-backend.up.railway.app` |

Replace with your actual Railway URL from Phase 10.

**Important:** No trailing slash!
- ✓ `https://your-backend.up.railway.app`
- ✗ `https://your-backend.up.railway.app/`

### Step 4: Deploy

1. Click **"Deploy"**
2. Watch the build logs
3. Wait for "Congratulations!" message
4. Click **"Visit"** to see your site

---

## 7. Understanding Vercel Build Logs

### Successful Build

```
Cloning github.com/username/link-previewer...
Cloning completed: 1.5s

Running "npm install"
added 145 packages in 3s

Running "npm run build"
vite v5.0.0 building for production...
✓ 30 modules transformed
dist/index.html                 0.46 kB
dist/assets/index-abc.js      195.61 kB

Build Completed: 15s

Deploying to production...
Deployment complete!
```

### Common Build Errors

**1. "Module not found"**
```
ERROR: Cannot find module 'react'
```
**Fix:** Ensure `npm install` ran. Check `package.json` has the dependency.

**2. "VITE_API_URL is undefined"**
```
TypeError: Cannot read property 'url' of undefined
```
**Fix:** Add `VITE_API_URL` to Vercel environment variables.

**3. "Build failed: exit code 1"**
Check for:
- TypeScript errors
- ESLint errors (if configured to fail on error)
- Import errors

---

## 8. Vercel Project Structure

### Dashboard Overview

```
Project: link-previewer
├── Production (main branch)
│   └── https://link-previewer.vercel.app
├── Preview (feature branches)
│   └── https://link-previewer-git-feature-xyz.vercel.app
└── Settings
    ├── General
    ├── Domains
    ├── Git
    ├── Functions
    └── Environment Variables
```

### Automatic Deployments

| Action | Result |
|--------|--------|
| Push to `main` | Production deployment |
| Push to other branch | Preview deployment |
| Open Pull Request | Preview deployment + comment with URL |
| Merge PR to `main` | New production deployment |

---

## 9. Custom Domains (Optional)

### Adding a Custom Domain

1. Go to **Settings** → **Domains**
2. Enter your domain (e.g., `linkpreviewer.com`)
3. Follow DNS configuration instructions

### Vercel's Free Subdomain

Every project gets:
- `your-project.vercel.app`
- HTTPS included
- No configuration needed

For learning, the free subdomain is perfect.

---

## 10. Updating the Backend CORS

### The Problem

After frontend deployment, you have:
```
Frontend: https://link-previewer.vercel.app
Backend:  https://link-previewer.up.railway.app
```

But the backend currently allows:
```python
ALLOWED_ORIGINS = "http://localhost:5173,http://localhost:3000"
```

CORS will block requests from your Vercel domain!

### The Fix

1. Go to **Railway dashboard**
2. Select your backend service
3. Go to **Variables**
4. Update `ALLOWED_ORIGINS`:
   ```
   https://link-previewer.vercel.app,http://localhost:5173
   ```
5. Railway auto-redeploys

**Important:** Include both production and localhost for continued local development.

---

## 11. Testing the Deployment

### Step 1: Open Your Vercel URL

Navigate to `https://your-project.vercel.app`

You should see the Link Previewer UI.

### Step 2: Test the Full Flow

1. Enter a URL: `https://github.com`
2. Click **"Preview"**
3. Should see loading spinner
4. Should see preview card with GitHub's metadata

### Step 3: Check DevTools

Open browser DevTools (F12) → Network tab:

**Successful request:**
```
Name:     unfurl
Status:   200
Type:     fetch
Domain:   your-backend.up.railway.app
```

**CORS error:**
```
Name:     unfurl
Status:   CORS error
Console:  Access to fetch... has been blocked by CORS policy
```

If CORS error, check Railway ALLOWED_ORIGINS includes your Vercel URL.

---

## 12. Troubleshooting

### Issue: "Failed to fetch"

**Symptoms:**
- UI shows error
- Network tab shows failed request

**Causes:**
1. **Wrong API URL** - Check `VITE_API_URL` in Vercel
2. **Backend down** - Check Railway deployment
3. **CORS error** - Check Railway ALLOWED_ORIGINS

**Debug steps:**
```
1. Open: https://your-backend.up.railway.app/health
   Should return: {"status": "healthy"}

2. Open: https://your-backend.up.railway.app/docs
   Should show Swagger UI

3. Check Vercel → Settings → Environment Variables
   VITE_API_URL should match your Railway URL
```

### Issue: "CORS Policy Error"

**Symptoms:**
- Console shows CORS error
- Network tab shows failed preflight

**Fix:**
1. Copy your Vercel URL
2. Go to Railway → Variables
3. Add to ALLOWED_ORIGINS (comma-separated, no trailing slash)
4. Wait for Railway to redeploy
5. Refresh your Vercel site

### Issue: "API URL is undefined"

**Symptoms:**
- Request goes to wrong URL
- Console shows `undefined/unfurl`

**Cause:** Environment variable not set or misspelled

**Fix:**
1. Vercel → Settings → Environment Variables
2. Ensure `VITE_API_URL` (exact spelling)
3. **Redeploy** after changing (build-time variables!)

### Issue: Build Works Locally but Fails on Vercel

**Common causes:**

1. **Case sensitivity:**
   - Windows: `App.jsx` = `app.jsx`
   - Linux (Vercel): `App.jsx` ≠ `app.jsx`
   - **Fix:** Match exact casing in imports

2. **Missing devDependency:**
   - Vercel runs `npm install` with `--production` sometimes
   - **Fix:** Move build tools to `dependencies`

3. **Different Node version:**
   - **Fix:** Add `"engines": { "node": "20.x" }` to package.json

---

## 13. Preview Deployments

### What Are Preview Deployments?

Every branch/PR gets its own URL:

```
main branch:        https://app.vercel.app
feature/dark-mode:  https://app-git-feature-dark-mode.vercel.app
fix/cors-bug:       https://app-git-fix-cors-bug.vercel.app
```

### Why They're Useful

1. **Test before merge** - Preview changes live
2. **Share with team** - Send URL for review
3. **Automatic** - No extra configuration
4. **Isolated** - Each PR has its own deployment

### Environment Variables for Previews

Vercel lets you set different variables for:
- Production (main branch)
- Preview (other branches)
- Development (local)

For most cases, same variables work for all.

---

## 14. Deployment Checklist

### Before Deployment

- [ ] Backend deployed and running (Railway)
- [ ] Backend URL noted
- [ ] Code pushed to GitHub
- [ ] `npm run build` works locally

### During Deployment

- [ ] Root Directory set to `frontend`
- [ ] `VITE_API_URL` set to Railway URL
- [ ] Build completes without errors

### After Deployment

- [ ] Site loads at Vercel URL
- [ ] Preview flow works (enter URL, see card)
- [ ] No CORS errors in console
- [ ] Updated Railway ALLOWED_ORIGINS with Vercel URL

---

## 15. Summary: Frontend Deployment Flow

```
1. Code pushed to GitHub
           ↓
2. Vercel detects push
           ↓
3. Vercel clones repo
           ↓
4. Vercel runs: npm install
           ↓
5. Vercel injects environment variables
           ↓
6. Vercel runs: npm run build
           ↓
7. Vite creates dist/ folder
           ↓
8. Vercel deploys dist/ to CDN
           ↓
9. CDN serves files globally
           ↓
10. Your site is live!
```

---

## 16. Self-Check Questions

1. **What's the difference between static and dynamic hosting?**

   Answer: Static hosting serves pre-built files (no server processing). Dynamic hosting runs code on every request. Static is faster and cheaper for frontend apps.

2. **Why are frontend environment variables less secure than backend?**

   Answer: Frontend variables are embedded at build time and shipped to the browser. Anyone can see them in DevTools. Backend variables stay on the server.

3. **What is a CDN and why does it make sites faster?**

   Answer: A CDN (Content Delivery Network) has servers worldwide. Users get files from the nearest server instead of one far away, reducing latency.

4. **Why do you need to redeploy after changing environment variables?**

   Answer: Vite embeds variables at build time. The built files have the old values. A rebuild is needed to embed the new values.

5. **What should you check if you see CORS errors after deployment?**

   Answer: Ensure the backend's `ALLOWED_ORIGINS` includes your Vercel URL. It needs the exact URL (with https://, without trailing slash).

6. **What's a preview deployment?**

   Answer: An automatic deployment for non-main branches. Every PR gets its own URL for testing changes before merging.

7. **Why shouldn't you put API keys in VITE_ environment variables?**

   Answer: VITE_ variables are embedded in the frontend JavaScript and visible to anyone. Secrets should only be in the backend.

8. **What happens if the root directory is wrong on Vercel?**

   Answer: Vercel won't find package.json or the build will fail. For our project, it needs to be set to `frontend`.

---

## Next Phase

With both frontend and backend deployed, we'll do final testing in **Phase 12: Final Integration & Testing**.

**Save your URLs:**
- Backend: `https://your-backend.up.railway.app`
- Frontend: `https://your-app.vercel.app`

