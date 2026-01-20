# Phase 8: Local Integration Testing - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- How to run multiple services locally
- How frontend and backend communicate
- How the Vite proxy works in development
- How to debug CORS issues
- Using browser DevTools for debugging
- Testing API endpoints manually
- Common integration issues and solutions

---

## 1. Running Both Services

### The Architecture

In development, we run two separate processes:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Computer                         │
│                                                         │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │         │   Backend    │             │
│  │  (Vite Dev)  │         │  (Uvicorn)   │             │
│  │              │         │              │             │
│  │ Port 5173    │ ──────> │ Port 8000    │             │
│  │              │  proxy  │              │             │
│  └──────────────┘         └──────────────┘             │
│         │                                               │
│         │                                               │
│  ┌──────────────┐                                      │
│  │   Browser    │                                      │
│  │              │                                      │
│  │ localhost:   │                                      │
│  │    5173      │                                      │
│  └──────────────┘                                      │
└─────────────────────────────────────────────────────────┘
```

### Step 1: Start the Backend

Open a terminal and run:

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd frontend

# Start the dev server
npm run dev
```

You should see:
```
  VITE v6.0.0  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

### Step 3: Open in Browser

Navigate to `http://localhost:5173` in your browser.

You should see the Link Previewer UI with:
- Title "Link Previewer"
- URL input field
- "Preview" button

---

## 2. Testing the Integration

### Test 1: Basic Flow

1. Enter a URL: `https://github.com`
2. Click "Preview"
3. You should see:
   - Loading spinner briefly
   - Preview card with GitHub's metadata
   - Title, description, image

### Test 2: Error Handling

1. Enter an invalid URL: `not-a-url`
2. Click "Preview"
3. You should see an error message

### Test 3: Network Error

1. Stop the backend (Ctrl+C in backend terminal)
2. Enter a URL and click "Preview"
3. You should see a connection error
4. Restart the backend

### Test 4: Various URLs

Try these URLs to test different scenarios:

| URL | Expected Result |
|-----|-----------------|
| `https://github.com` | Full preview with image |
| `https://google.com` | Minimal preview (no og tags) |
| `https://www.youtube.com/watch?v=dQw4w9WgXcQ` | Video preview with thumbnail |
| `https://twitter.com` | Twitter preview |
| `https://invalid.domain.fake` | DNS error |
| `https://httpstat.us/404` | HTTP 404 error |
| `https://httpstat.us/500` | HTTP 500 error |

---

## 3. Understanding the Proxy

### The Problem: Browsers Block Cross-Origin Requests

When you run the app locally, you have two servers:

```
Your browser opens:      http://localhost:5173  (frontend)
Your API runs at:        http://localhost:8000  (backend)
```

Even though both are on "localhost", the **different port numbers** make them different "origins" in the browser's eyes.

Browsers have a security feature called the **Same-Origin Policy**. It blocks web pages from making requests to different origins. This prevents malicious websites from stealing your data from other sites.

Without any solution, you'd see this error:

```
Access to fetch at 'http://localhost:8000/unfurl' from origin
'http://localhost:5173' has been blocked by CORS policy
```

### The Solution: A Middleman (Proxy)

A proxy is a middleman that forwards requests. Here's the difference:

**Without proxy - BLOCKED:**
```
┌─────────────┐                           ┌─────────────┐
│   Browser   │ ─────── BLOCKED! ───────→ │   Backend   │
│             │                           │             │
│ localhost:  │   Browser says: "Nope,    │ localhost:  │
│    5173     │   different origin!"      │    8000     │
└─────────────┘                           └─────────────┘
```

**With proxy - WORKS:**
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │ ───→ │ Vite Server │ ───→ │   Backend   │
│             │      │ (middleman) │      │             │
│ localhost:  │      │ localhost:  │      │ localhost:  │
│    5173     │      │    5173     │      │    8000     │
└─────────────┘      └─────────────┘      └─────────────┘
                            ↑
                    Browser thinks it's
                    talking to :5173
                    (same origin = allowed!)
```

### How It Works in Plain English

1. Your React code asks for `/api/unfurl`
2. The request goes to the Vite dev server (port 5173)
3. Vite sees the `/api` prefix and thinks: "I should forward this!"
4. Vite sends the request to the backend (port 8000)
5. The backend responds to Vite
6. Vite passes the response back to your browser
7. Your browser is happy - it thinks everything stayed on port 5173

**The browser never knows about port 8000.** As far as it's concerned, everything is same-origin.

### The Configuration

This magic is configured in `frontend/vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

**What each part does:**

| Setting | Meaning |
|---------|---------|
| `'/api'` | "Intercept any request starting with /api" |
| `target` | "Forward it to this server" |
| `changeOrigin` | "Pretend the request came from the target" |
| `rewrite` | "Remove the /api prefix before forwarding" |

### Why Remove the `/api` Prefix?

The frontend uses `/api/unfurl` but the backend endpoint is just `/unfurl`.

The `/api` prefix is only used to tell Vite "this should be proxied." The backend doesn't need it.

```
Frontend calls:     /api/unfurl
Vite removes /api:  /unfurl
Backend receives:   /unfurl  ✓
```

**Example transformations:**

| Frontend Request | Backend Receives |
|------------------|------------------|
| `/api/unfurl` | `/unfurl` |
| `/api/health` | `/health` |
| `/api/docs` | `/docs` |

### The Complete Journey of a Request

```
1. You click "Preview" in the browser

2. React code runs: fetch('/api/unfurl', { body: {url: '...'} })

3. Browser sends request to: http://localhost:5173/api/unfurl
   (same origin as the page - allowed!)

4. Vite dev server receives the request
   - Sees it starts with '/api'
   - Removes '/api' prefix → '/unfurl'
   - Forwards to http://localhost:8000/unfurl

5. Backend processes the request
   - Fetches the URL
   - Extracts metadata
   - Returns JSON response

6. Vite receives the backend's response

7. Vite sends the response back to the browser

8. React updates the UI with the preview card
```

---

## 4. Using Browser DevTools

### Opening DevTools

- **Windows/Linux:** F12 or Ctrl+Shift+I
- **Mac:** Cmd+Option+I
- **Right-click:** "Inspect" → DevTools

### Network Tab

The Network tab shows all HTTP requests:

1. Open DevTools → Network tab
2. Make a request in the app
3. Look for the `/api/unfurl` request
4. Click to see details:
   - **Headers:** Request/response headers
   - **Payload:** What was sent (request body)
   - **Response:** What came back (JSON)
   - **Timing:** How long each phase took

### What to Look For

**Successful request:**
```
Status: 200 OK
Response: {"success": true, "data": {...}}
```

**Failed request:**
```
Status: 422 Unprocessable Entity
Response: {"detail": [{"msg": "Invalid URL", ...}]}
```

**Network error:**
```
Status: (failed)
Type: Failed to fetch
```

### Console Tab

The Console shows JavaScript errors and logs:

```javascript
// In your code
console.log('API response:', data)

// Shows in Console:
// API response: {success: true, data: {...}}
```

### Common Issues in DevTools

| What You See | Likely Cause |
|--------------|--------------|
| Red request, "CORS error" | Proxy not working or backend down |
| 404 Not Found | Wrong endpoint path |
| 422 Unprocessable Entity | Validation error (check Payload) |
| 500 Internal Server Error | Bug in backend code |
| "(failed)" | Backend not running or network issue |

---

## 5. Debugging CORS Issues

### Symptom

```
Access to fetch at 'http://localhost:8000/unfurl' from origin
'http://localhost:5173' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present
```

### Cause 1: Calling Backend Directly

**Wrong (bypassing proxy):**
```javascript
fetch('http://localhost:8000/unfurl', ...)  // Direct call!
```

**Right (using proxy):**
```javascript
fetch('/api/unfurl', ...)  // Goes through Vite proxy
```

### Cause 2: Backend Not Running

If the backend isn't running, the proxy fails and you might see CORS errors.

**Fix:** Start the backend: `uvicorn app.main:app --reload`

### Cause 3: Proxy Not Configured

Check `vite.config.js` has the proxy configuration.

### Cause 4: Wrong Proxy Path

If your code calls `/unfurl` but proxy is configured for `/api`:

**Wrong:**
```javascript
fetch('/unfurl', ...)  // Not matched by proxy
```

**Right:**
```javascript
fetch('/api/unfurl', ...)  // Matched by /api proxy rule
```

---

## 6. Testing the API Directly

### Using the Browser

Visit `http://localhost:8000/docs` to access Swagger UI:

1. Find the POST `/unfurl` endpoint
2. Click "Try it out"
3. Enter: `{"url": "https://github.com"}`
4. Click "Execute"
5. See the response

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Unfurl a URL
curl -X POST http://localhost:8000/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

### Using Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/unfurl",
    json={"url": "https://github.com"}
)
print(response.json())
```

### Using JavaScript (Node.js)

```javascript
const response = await fetch('http://localhost:8000/unfurl', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://github.com' })
});
const data = await response.json();
console.log(data);
```

---

## 7. Common Integration Issues

### Issue: "Failed to fetch"

**Symptoms:**
- Error message: "Failed to fetch" or similar
- Network tab shows "(failed)"

**Causes:**
1. Backend not running
2. Backend crashed
3. Wrong port

**Fix:**
- Check backend terminal for errors
- Restart backend: `uvicorn app.main:app --reload`
- Verify port 8000: `curl http://localhost:8000/health`

### Issue: "CORS Error"

**Symptoms:**
- Console shows CORS policy error
- Request blocked by browser

**Fix:**
- Ensure using `/api/` prefix in fetch calls
- Check Vite proxy configuration
- Verify backend is running

### Issue: "404 Not Found"

**Symptoms:**
- Status code 404
- Endpoint not found

**Causes:**
1. Wrong endpoint path
2. Missing `/api` prefix
3. Typo in URL

**Fix:**
- Check endpoint matches backend: `/api/unfurl` → `/unfurl`
- Verify in Swagger UI: `http://localhost:8000/docs`

### Issue: "422 Unprocessable Entity"

**Symptoms:**
- Status code 422
- Validation error

**Causes:**
1. Invalid URL format
2. Missing required field
3. Wrong data type

**Fix:**
- Check request body in Network tab
- Ensure URL includes protocol (`https://`)
- Verify JSON structure matches API spec

### Issue: Slow Responses

**Symptoms:**
- Preview takes a long time
- Sometimes times out

**Causes:**
1. Target website is slow
2. Target website blocks requests
3. Network issues

**Fix:**
- Try different URLs
- Check timeout settings in backend
- Verify network connectivity

---

## 8. Development Workflow

### Typical Development Session

1. **Start backend:**
   ```bash
   cd backend
   venv\Scripts\activate  # or source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser:** `http://localhost:5173`

4. **Make changes:**
   - Backend changes: Uvicorn auto-reloads
   - Frontend changes: Vite hot-reloads

5. **Test changes:** Refresh or use HMR

### Watching Logs

**Backend logs:**
```
INFO:     127.0.0.1:54321 - "POST /unfurl HTTP/1.1" 200 OK
```

**Frontend logs:**
- Browser console for JavaScript
- Terminal for build errors

### Hot Reload

Both servers support hot reload:

- **Uvicorn `--reload`:** Restarts on Python file changes
- **Vite HMR:** Updates browser without refresh

This means you rarely need to restart servers during development.

---

## 9. Integration Checklist

### Backend

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server running on port 8000
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/unfurl` endpoint accepts POST requests
- [ ] CORS configured for localhost:5173

### Frontend

- [ ] Dependencies installed (`npm install`)
- [ ] Dev server running on port 5173
- [ ] Proxy configured in `vite.config.js`
- [ ] API calls use `/api/` prefix
- [ ] Error handling works

### Integration

- [ ] Frontend can reach backend through proxy
- [ ] No CORS errors in console
- [ ] Preview card displays correctly
- [ ] Error messages show for invalid URLs
- [ ] Loading state works

---

## 10. Commands Reference

### Backend Commands

```bash
# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Mac/Linux)
source venv/bin/activate

# Start server
uvicorn app.main:app --reload

# Start with specific host/port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run without reload (production-like)
uvicorn app.main:app

# Check if running
curl http://localhost:8000/health
```

### Frontend Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing Commands

```bash
# Test backend directly
curl http://localhost:8000/health
curl -X POST http://localhost:8000/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'

# Check port usage (Windows)
netstat -an | findstr :8000
netstat -an | findstr :5173

# Check port usage (Mac/Linux)
lsof -i :8000
lsof -i :5173
```

---

## 11. Self-Check Questions

1. **Why do we need two terminals to run the full application?**

   Answer: Frontend (Vite) and backend (Uvicorn) are separate processes that need to run simultaneously. Each needs its own terminal to show logs and accept Ctrl+C to stop.

2. **What does the Vite proxy do?**

   Answer: It forwards requests from `/api/*` to the backend server, making them appear as same-origin requests to the browser. This avoids CORS issues during development.

3. **Why does `/api/unfurl` become `/unfurl` on the backend?**

   Answer: The proxy's `rewrite` function removes the `/api` prefix. The frontend uses `/api` to identify proxy-able requests, but the backend doesn't have that prefix.

4. **How do you check if the backend is running?**

   Answer: Try `curl http://localhost:8000/health` or open `http://localhost:8000/docs` in a browser. You should see a response or the Swagger UI.

5. **What causes "Failed to fetch" errors?**

   Answer: Usually the backend isn't running. Could also be wrong port, network issues, or the backend crashed. Check the backend terminal for errors.

6. **Where do you see API requests in DevTools?**

   Answer: Network tab. Click on a request to see headers, payload (request body), response, and timing.

7. **Why might the preview card not show an image?**

   Answer: The website might not have an og:image tag, the image URL might be invalid, or the image might fail to load (CORS, 404). The onError handler hides broken images.

8. **What is Hot Module Replacement (HMR)?**

   Answer: A Vite feature that updates changed modules in the browser without a full page refresh, preserving application state. Makes development faster.

---

## Next Phase

Now that everything works locally, we will prepare for deployment in **Phase 9: Deployment Preparation**.
