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

| Static (Vercel, Netlify) | Dynamic (Render, Railway) |
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

**Runtime variables (Backend - Render):**
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
const apiUrl = "https://your-api.onrender.com";
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
- [ ] Backend deployed on Render (from Phase 10)
- [ ] Your Render API URL (e.g., `https://your-app.onrender.com`)
- [ ] A Vercel account (we'll create this)

---

## 5. Step-by-Step Deployment

### Step 1: Create Vercel Account

**Option A: Sign up with GitHub (Recommended)**
1. Go to **https://vercel.com**
2. Click **"Sign Up"** (top right)
3. Click **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub
5. You're logged in!

**Option B: Sign up with Email**
1. Go to **https://vercel.com**
2. Click **"Sign Up"** (top right)
3. Enter your email address
4. Check email for 6-digit verification code
5. Enter the code to complete signup
6. **Important:** When asked about your plan, select **"I'm working on personal projects"** to get the free Hobby tier
7. You may be asked to enter your name - fill in your preferred display name

### Step 2: Import Your Project

1. From the Vercel dashboard, click **"Add New..."** button
2. Select **"Project"** from the dropdown
3. You'll see a list of your GitHub repositories
4. Find your repository (e.g., `link-previewer`)
5. Click **"Import"** next to it

**If you don't see your repository:**
- Click **"Adjust GitHub App Permissions"**
- Grant Vercel access to the specific repository
- Return to Vercel and refresh

### Step 3: Configure Project Settings

Vercel shows you the configuration screen. Configure as follows:

**Project Name:**
- Leave default or customize (this becomes your URL subdomain)

**Framework Preset:**
- Vercel auto-detects **Vite** - leave as is

**Root Directory:**
1. Click **"Edit"** next to Root Directory
2. A file browser dialog will appear showing your repo structure
3. You'll see folders like `backend`, `docs`, `frontend`
4. Click on **`frontend`** to select it (it will be highlighted)
5. Click the **"Continue"** button at the bottom of the dialog
6. The dialog closes and you'll see "frontend" displayed as the Root Directory

**Build and Output Settings:**
Usually auto-detected correctly:
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

### Step 4: Add Environment Variables

**This is critical!** Your frontend needs to know where the backend is.

1. Scroll down to **"Environment Variables"** section
2. Click to expand it
3. Add the following variable:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://your-backend.onrender.com` |

**To add the variable:**
1. Click in the **"Key"** field
2. Type: `VITE_API_URL`
3. Click in the **"Value"** field
4. Type your Render backend URL (e.g., `https://link-previewer-ehwf.onrender.com`)
5. Leave **"Production"** checkbox checked (default)

**Important:**
- No trailing slash! ✓ `https://api.onrender.com` ✗ `https://api.onrender.com/`
- Use your actual Render URL from Phase 10
- The key must start with `VITE_` for Vite to expose it

**Troubleshooting tip:** If a search popup appears while typing, press **Escape** to close it and make sure you're clicking directly in the input field (not elsewhere on the page)

### Step 5: Deploy

1. Click the **"Deploy"** button
2. Watch the build progress:
   - Cloning repository...
   - Installing dependencies...
   - Building...
   - Deploying...
3. Wait for **"Congratulations!"** message (about 1-2 minutes)
4. Click **"Continue to Dashboard"** or **"Visit"** to see your site

### Step 6: Get Your Frontend URL

Your frontend URL is displayed at the top of the project dashboard:
```
https://your-project-name.vercel.app
```

Example: `https://link-previewer-smoky.vercel.app`

**Save this URL!** You'll need it for the next step.

---

## 6. Configure Backend CORS (Critical!)

### The Problem

Right now:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.onrender.com`

But the backend only allows localhost by default:
```python
ALLOWED_ORIGINS = "http://localhost:5173,http://localhost:3000"
```

**Your frontend requests will be blocked by CORS!**

### The Solution: Add Vercel URL to Render

1. Go to **https://dashboard.render.com**
2. You'll see your projects listed - click on **"My project"** (or your project group name)
3. Click on your backend service (e.g., `link-previewer`)
4. Click **"Environment"** in the left sidebar
5. Click the **"+ Add"** button
6. Select **"New variable"** from the dropdown
7. Enter:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** `https://your-app.vercel.app,http://localhost:5173,http://localhost:3000`
8. Click **"Save, rebuild, and deploy"**

**To verify deployment:**
- Click **"Events"** in the left sidebar
- Wait for "Deploy live" status (usually 1-2 minutes)

**Example value:**
```
https://link-previewer-smoky.vercel.app,http://localhost:5173,http://localhost:3000
```

**Important notes:**
- Use your actual Vercel URL
- No trailing slashes
- Include localhost URLs for local development
- Comma-separated, no spaces

### Wait for Redeploy

After saving, Render automatically redeploys your backend. Wait for the deployment to complete (check the "Events" tab).

---

## 7. Test the Complete Integration

### Test 1: Load the Frontend

1. Open your Vercel URL in a browser
2. You should see the Link Previewer interface:
   - Title: "Link Previewer"
   - URL input field
   - "Preview" button

### Test 2: Preview a URL

1. Enter a URL: `https://github.com`
2. Click **"Preview"**
3. Wait for the response (may take ~50 seconds if backend is cold)
4. You should see a preview card with:
   - Site name
   - Title
   - Description
   - Image (if available)

### Test 3: Check for Errors

Open browser DevTools (F12) → Console tab:

**If working:** No errors
**If CORS error:** You'll see:
```
Access to fetch at 'https://...' from origin 'https://...'
has been blocked by CORS policy
```

### Test 4: Check Network Tab

Open DevTools → Network tab → Make a request:

**Successful request:**
- Status: 200
- Response: JSON with metadata

**Failed request:**
- Status: CORS error or 503
- Check backend is running and CORS is configured

---

## 8. Understanding Vercel Build Logs

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

## 9. Preview Deployments

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

---

## 10. Troubleshooting

### Issue: "Failed to fetch"

**Symptoms:**
- UI shows error message
- Network tab shows failed request

**Causes and fixes:**

1. **Backend is sleeping (503 error)**
   - Render free tier sleeps after 15 minutes
   - Visit `/health` endpoint to wake it up
   - Wait ~50 seconds for cold start
   - Try again

2. **Wrong API URL**
   - Go to Vercel → Settings → Environment Variables
   - Verify `VITE_API_URL` matches your Render URL
   - **After changing: Redeploy!** (build-time variable)

3. **CORS not configured**
   - Go to Render → Environment
   - Add/update `ALLOWED_ORIGINS` with your Vercel URL
   - Wait for Render to redeploy

### Issue: "CORS Policy Error"

**Symptoms:**
- Console shows CORS error
- Network tab shows failed preflight (OPTIONS request)

**Fix:**
1. Copy your exact Vercel URL (e.g., `https://link-previewer-smoky.vercel.app`)
2. Go to Render dashboard → your service → Environment
3. Add environment variable:
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://your-app.vercel.app,http://localhost:5173,http://localhost:3000`
4. Wait for Render to redeploy
5. Refresh your Vercel site and test again

### Issue: "API URL is undefined"

**Symptoms:**
- Request goes to wrong URL
- Console shows `undefined/unfurl`

**Fix:**
1. Go to Vercel → Settings → Environment Variables
2. Ensure `VITE_API_URL` is set (exact spelling with underscore)
3. **Important:** Click "Redeploy" after changing (build-time variables require rebuild)

### Issue: Build Works Locally but Fails on Vercel

**Common causes:**

1. **Case sensitivity:**
   - Windows: `App.jsx` = `app.jsx`
   - Linux (Vercel): `App.jsx` ≠ `app.jsx`
   - **Fix:** Match exact casing in imports

2. **Missing devDependency:**
   - **Fix:** Move build tools to `dependencies`

3. **Different Node version:**
   - **Fix:** Add `"engines": { "node": "20.x" }` to package.json

---

## 11. Quick Reference

### Your Deployment Settings

| Setting | Value |
|---------|-------|
| Platform | Vercel |
| Framework | Vite (auto-detected) |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

### Environment Variables

| Variable | Where to Set | Value |
|----------|--------------|-------|
| `VITE_API_URL` | Vercel | Your Render backend URL |
| `ALLOWED_ORIGINS` | Render | Your Vercel frontend URL + localhost |

### Important URLs

| URL | Purpose |
|-----|---------|
| `https://your-app.vercel.app` | Your frontend |
| `https://your-backend.onrender.com` | Your backend API |
| `https://your-backend.onrender.com/docs` | API documentation |

---

## 12. Deployment Checklist

### Before Deployment

- [ ] Backend deployed and running on Render
- [ ] Backend URL noted (e.g., `https://xxx.onrender.com`)
- [ ] Code pushed to GitHub
- [ ] `npm run build` works locally

### During Deployment

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root Directory set to `frontend`
- [ ] `VITE_API_URL` environment variable added
- [ ] Build completes without errors

### After Deployment

- [ ] Site loads at Vercel URL
- [ ] Updated Render `ALLOWED_ORIGINS` with Vercel URL
- [ ] Preview flow works (enter URL → see card)
- [ ] No CORS errors in browser console

---

## 13. Self-Check Questions

1. **What's the difference between static and dynamic hosting?**

   Answer: Static hosting serves pre-built files (no server processing). Dynamic hosting runs code on every request. Static is faster and cheaper for frontend apps.

2. **Why are frontend environment variables less secure than backend?**

   Answer: Frontend variables are embedded at build time and shipped to the browser. Anyone can see them in DevTools. Backend variables stay on the server.

3. **What is a CDN and why does it make sites faster?**

   Answer: A CDN (Content Delivery Network) has servers worldwide. Users get files from the nearest server instead of one far away, reducing latency.

4. **Why do you need to redeploy after changing environment variables on Vercel?**

   Answer: Vite embeds variables at build time. The built files have the old values. A rebuild is needed to embed the new values.

5. **What should you check if you see CORS errors after deployment?**

   Answer: Ensure the backend's `ALLOWED_ORIGINS` on Render includes your Vercel URL. It needs the exact URL (with https://, without trailing slash).

---

## Next Phase

With both frontend and backend deployed, proceed to **Phase 12: Final Integration & Testing** to verify everything works together.

**Save your URLs:**
- Backend: `https://________________________.onrender.com`
- Frontend: `https://________________________.vercel.app`
