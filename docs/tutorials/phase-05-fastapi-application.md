# Phase 5: FastAPI Application - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- How web frameworks work (request → handler → response)
- What FastAPI is and why it's popular
- How to define API routes and endpoints
- What CORS is and why browsers need it
- How middleware works in web applications
- Error handling patterns for APIs
- How to run and test your API locally

---

## 1. How Web APIs Work

### The Request-Response Cycle

Every web API follows this basic pattern:

```
Client (Browser/App)          Server (Your API)
       │                            │
       │  1. HTTP Request           │
       │  POST /unfurl              │
       │  {"url": "https://..."}    │
       │ ─────────────────────────> │
       │                            │
       │                      2. Process Request
       │                         - Validate input
       │                         - Run business logic
       │                         - Prepare response
       │                            │
       │  3. HTTP Response          │
       │  200 OK                    │
       │  {"success": true, ...}    │
       │ <───────────────────────── │
       │                            │
```

### HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve data | Get user profile |
| POST | Create/Submit data | Create new user, Submit form |
| PUT | Update (replace) | Update entire user record |
| PATCH | Update (partial) | Update just email |
| DELETE | Remove data | Delete user |

Our `/unfurl` endpoint uses POST because we're submitting a URL for processing.

### HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | New resource created |
| 400 | Bad Request | Client sent invalid data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Not allowed to access |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable | Valid JSON but invalid data |
| 500 | Server Error | Something broke on server |

---

## 2. What is FastAPI?

### Overview

FastAPI is a modern Python web framework for building APIs. It was created in 2018 and has rapidly become one of the most popular Python frameworks.

### Why FastAPI?

**1. Speed**
- One of the fastest Python frameworks
- Comparable to Node.js and Go
- Uses async/await for concurrent requests

**2. Automatic Validation**
- Uses Pydantic models for input validation
- Bad requests automatically return 422 errors
- No manual validation code needed

**3. Automatic Documentation**
- Generates OpenAPI (Swagger) spec automatically
- Interactive docs at `/docs`
- Alternative docs at `/redoc`

**4. Type Hints**
- Full IDE support (autocomplete, error checking)
- Self-documenting code
- Catches errors early

**5. Easy to Learn**
- Intuitive, decorator-based routing
- Excellent documentation
- Familiar to Flask users

### FastAPI vs Other Frameworks

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Speed | Very Fast | Medium | Slower |
| Async | Native | Extension | Extension |
| Validation | Built-in (Pydantic) | Manual | Manual/Forms |
| Auto Docs | Yes | No | No |
| Learning Curve | Easy | Easy | Steep |
| Batteries | Minimal | Minimal | Many |

FastAPI is ideal for APIs. Django is better for full web apps with templates.

---

## 3. Creating a FastAPI Application

### Basic Application

```python
from fastapi import FastAPI

# Create the application instance
app = FastAPI()

# Define a route
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```

That's it! A complete API in 7 lines.

### Application Configuration

```python
app = FastAPI(
    title="Link Previewer API",        # Shown in docs
    description="Extract metadata...",  # Shown in docs
    version="1.0.0",                   # API version
    docs_url="/docs",                  # Swagger UI path
    redoc_url="/redoc",                # ReDoc path
)
```

### The Decorator Pattern

```python
@app.get("/users")        # GET /users
@app.post("/users")       # POST /users
@app.get("/users/{id}")   # GET /users/123
@app.put("/users/{id}")   # PUT /users/123
@app.delete("/users/{id}") # DELETE /users/123
```

The decorator (`@app.get(...)`) tells FastAPI:
- What HTTP method to respond to
- What URL path to match
- Which function handles the request

---

## 4. Defining Routes (Endpoints)

### Simple GET Route

```python
@app.get("/")
def root():
    return {"message": "Hello"}
```

- `@app.get("/")` - Respond to GET requests at "/"
- `def root()` - Function that handles the request
- `return {"message": "Hello"}` - FastAPI converts dict to JSON

### Route with Path Parameters

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

- `{user_id}` in path becomes a function parameter
- `: int` validates and converts to integer
- GET /users/123 → `{"user_id": 123}`
- GET /users/abc → 422 error (not an integer)

### Route with Query Parameters

```python
@app.get("/search")
def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}
```

- `q: str` - Required query parameter
- `limit: int = 10` - Optional with default
- GET /search?q=hello → `{"query": "hello", "limit": 10}`
- GET /search?q=hello&limit=5 → `{"query": "hello", "limit": 5}`
- GET /search → 422 error (missing q)

### Route with Request Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

- `item: Item` - FastAPI reads JSON body and validates against Item model
- POST /items with `{"name": "Widget", "price": 9.99}` → Works
- POST /items with `{"name": "Widget"}` → 422 error (missing price)

### Our /unfurl Endpoint

```python
@app.post("/unfurl", response_model=UnfurlResponse)
async def unfurl(request: UnfurlRequest) -> UnfurlResponse:
    url_str = str(request.url)
    try:
        data = await unfurl_url(url_str)
        return UnfurlResponse(success=True, data=data)
    except Exception as e:
        return UnfurlResponse(success=False, error=str(e))
```

Breaking it down:
- `@app.post("/unfurl")` - POST requests to /unfurl
- `response_model=UnfurlResponse` - Validates and documents response
- `async def` - Async function (can use await)
- `request: UnfurlRequest` - Validates JSON body
- `-> UnfurlResponse` - Return type hint

---

## 5. Understanding CORS

### What is CORS?

CORS (Cross-Origin Resource Sharing) is a browser security feature that blocks web pages from making requests to different domains.

### Why Does CORS Exist?

Imagine you're logged into your bank at `bank.com`. You visit `evil.com`. Without CORS, evil.com's JavaScript could:

```javascript
// On evil.com
fetch("https://bank.com/api/transfer", {
    method: "POST",
    body: JSON.stringify({to: "hacker", amount: 10000}),
    credentials: "include"  // Sends your bank cookies!
});
```

CORS prevents this by requiring servers to explicitly allow cross-origin requests.

### How CORS Works

```
1. Browser: "I'm on localhost:5173, can I call localhost:8000?"

2. Browser sends "preflight" request:
   OPTIONS /unfurl
   Origin: http://localhost:5173

3. Server responds with CORS headers:
   Access-Control-Allow-Origin: http://localhost:5173
   Access-Control-Allow-Methods: POST
   Access-Control-Allow-Headers: Content-Type

4. Browser: "Server says OK, I'll allow the actual request"

5. Browser sends actual request:
   POST /unfurl
   Origin: http://localhost:5173
```

### CORS Errors

Without proper CORS configuration, you'll see:

```
Access to fetch at 'http://localhost:8000/unfurl' from origin
'http://localhost:5173' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

This is the browser blocking the request, not the server rejecting it.

### Configuring CORS in FastAPI

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],     # Allow all methods
    allow_headers=["*"],     # Allow all headers
)
```

**allow_origins**: List of URLs that can call your API
- `["http://localhost:5173"]` - Only this URL
- `["*"]` - Any URL (use in development only!)

**allow_credentials**: Whether to allow cookies/auth headers
- `True` for authenticated APIs

**allow_methods**: Which HTTP methods to allow
- `["GET", "POST"]` - Only these
- `["*"]` - All methods

**allow_headers**: Which headers clients can send
- `["*"]` - All headers (common choice)

### Our CORS Configuration

```python
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

We use an environment variable so we can change allowed origins without changing code:
- Development: `http://localhost:5173`
- Production: `https://your-frontend.vercel.app`

---

## 6. Middleware Explained

### What is Middleware?

Middleware is code that runs before and/or after every request. It's like a pipeline:

```
Request → Middleware 1 → Middleware 2 → Route Handler
                                              ↓
Response ← Middleware 1 ← Middleware 2 ← Response
```

### Common Middleware Uses

| Middleware | Purpose |
|------------|---------|
| CORS | Add CORS headers |
| Authentication | Check auth tokens |
| Logging | Log all requests |
| Compression | Gzip responses |
| Rate Limiting | Prevent abuse |
| Error Handling | Catch exceptions |

### How CORS Middleware Works

```python
class CORSMiddleware:
    async def __call__(self, request, call_next):
        # Before request: Check if it's a preflight OPTIONS request
        if request.method == "OPTIONS":
            return Response(headers=cors_headers)

        # Call the actual route handler
        response = await call_next(request)

        # After response: Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        return response
```

Every request goes through this middleware, getting CORS headers added automatically.

### Adding Multiple Middleware

```python
# Order matters! First added = outermost
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(GZipMiddleware)
app.add_middleware(AuthMiddleware)

# Request flow:
# CORS → GZip → Auth → Handler → Auth → GZip → CORS
```

---

## 7. Error Handling

### Why Proper Error Handling Matters

Bad error handling:
```python
@app.post("/unfurl")
async def unfurl(request: UnfurlRequest):
    data = await unfurl_url(str(request.url))  # Might raise!
    return data  # Never reached if error
```

If `unfurl_url` raises an exception, the client gets:
```json
{
    "detail": "Internal Server Error"
}
```

No useful information about what went wrong.

### Good Error Handling

```python
@app.post("/unfurl")
async def unfurl(request: UnfurlRequest):
    try:
        data = await unfurl_url(str(request.url))
        return UnfurlResponse(success=True, data=data)

    except httpx.TimeoutException:
        return UnfurlResponse(
            success=False,
            error="Request timed out"
        )

    except httpx.HTTPStatusError as e:
        return UnfurlResponse(
            success=False,
            error=f"HTTP error {e.response.status_code}"
        )
```

Now the client gets actionable error messages.

### Our Error Handling Strategy

```python
@app.post("/unfurl")
async def unfurl(request: UnfurlRequest) -> UnfurlResponse:
    url_str = str(request.url)

    try:
        data = await unfurl_url(url_str)
        return UnfurlResponse(success=True, data=data)

    except httpx.TimeoutException:
        # Network timeout
        return UnfurlResponse(
            success=False,
            error=f"Request timed out while fetching {url_str}"
        )

    except httpx.HTTPStatusError as e:
        # Server returned 4xx/5xx
        return UnfurlResponse(
            success=False,
            error=f"HTTP error {e.response.status_code} while fetching {url_str}"
        )

    except httpx.RequestError as e:
        # Network error (DNS, connection refused, etc.)
        return UnfurlResponse(
            success=False,
            error=f"Failed to connect to {url_str}: {type(e).__name__}"
        )

    except ValueError as e:
        # Our custom validation errors
        return UnfurlResponse(
            success=False,
            error=str(e)
        )

    except Exception as e:
        # Unexpected error - log and return generic message
        print(f"Unexpected error: {e}")
        return UnfurlResponse(
            success=False,
            error="An unexpected error occurred"
        )
```

**Key principles:**
1. Catch specific exceptions first
2. Provide helpful error messages
3. Log unexpected errors
4. Never expose internal details to clients
5. Always return a valid response

### HTTP Status Codes for Errors

Our API always returns 200 with `success: false` for business errors. An alternative approach:

```python
from fastapi import HTTPException

@app.post("/unfurl")
async def unfurl(request: UnfurlRequest):
    try:
        data = await unfurl_url(str(request.url))
        return {"data": data}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e.response.status_code}")
```

Both approaches are valid. We chose 200 + success flag for simpler client handling.

---

## 8. Health Check Endpoint

### Why Health Checks?

Deployment platforms need to know if your service is healthy:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### How Platforms Use Health Checks

**Railway/Kubernetes:**
```yaml
healthcheck:
  path: /health
  interval: 30s
  timeout: 5s
```

Every 30 seconds, the platform calls `/health`. If it fails:
1. First failure: Mark as unhealthy
2. Multiple failures: Restart the container
3. During deployment: Don't route traffic until healthy

### Advanced Health Checks

```python
@app.get("/health")
async def health_check():
    # Check database connection
    try:
        await db.execute("SELECT 1")
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "database"}
        )

    # Check external service
    try:
        async with httpx.AsyncClient() as client:
            await client.get("https://api.example.com/health", timeout=2.0)
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "external_api"}
        )

    return {"status": "healthy"}
```

Our simple API doesn't need this, but it's good to know.

---

## 9. Running the Application

### Development Server

```bash
# From the backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `app.main:app` - Module path : variable name
- `--reload` - Auto-restart on code changes
- `--host 0.0.0.0` - Accept connections from any IP
- `--port 8000` - Listen on port 8000

### Testing the API

**Using curl:**
```bash
# Test root
curl http://localhost:8000/

# Test health
curl http://localhost:8000/health

# Test unfurl
curl -X POST http://localhost:8000/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

**Using Python:**
```python
import httpx

# Test unfurl
response = httpx.post(
    "http://localhost:8000/unfurl",
    json={"url": "https://github.com"}
)
print(response.json())
```

**Using the browser:**
- Open http://localhost:8000/ - See API info
- Open http://localhost:8000/docs - Interactive Swagger UI
- Open http://localhost:8000/redoc - Alternative documentation

### Automatic Documentation

FastAPI generates interactive documentation automatically!

**Swagger UI (/docs):**
- Try out endpoints directly
- See request/response schemas
- View all available endpoints

**ReDoc (/redoc):**
- Clean, readable documentation
- Good for sharing with others
- Generated from OpenAPI spec

---

## 10. The Complete main.py

```python
"""
FastAPI Application for the Link Previewer API.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .models import UnfurlRequest, UnfurlResponse
from .unfurl import unfurl_url

# Create application
app = FastAPI(
    title="Link Previewer API",
    description="Extract metadata from URLs",
    version="1.0.0",
)

# Configure CORS
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {"name": "Link Previewer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/unfurl", response_model=UnfurlResponse)
async def unfurl(request: UnfurlRequest) -> UnfurlResponse:
    try:
        data = await unfurl_url(str(request.url))
        return UnfurlResponse(success=True, data=data)
    except httpx.TimeoutException:
        return UnfurlResponse(success=False, error="Request timed out")
    except httpx.HTTPStatusError as e:
        return UnfurlResponse(success=False, error=f"HTTP {e.response.status_code}")
    except Exception as e:
        return UnfurlResponse(success=False, error=str(e))

# Run with: uvicorn app.main:app --reload
```

---

## 11. Commands Reference

### FastAPI Application

```python
from fastapi import FastAPI

# Create app
app = FastAPI(title="My API", version="1.0.0")

# Routes
@app.get("/path")
@app.post("/path")
@app.put("/path/{id}")
@app.delete("/path/{id}")

# With response model
@app.post("/path", response_model=MyModel)

# Status code
@app.post("/path", status_code=201)

# Middleware
app.add_middleware(MiddlewareClass, **options)
```

### Uvicorn Commands

```bash
# Basic run
uvicorn app.main:app

# Development (with reload)
uvicorn app.main:app --reload

# Specify host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Multiple workers (production)
uvicorn app.main:app --workers 4

# With SSL
uvicorn app.main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### Testing Commands

```bash
# GET request
curl http://localhost:8000/

# POST with JSON
curl -X POST http://localhost:8000/unfurl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# With verbose output
curl -v http://localhost:8000/

# See response headers
curl -I http://localhost:8000/
```

---

## 12. Self-Check Questions

1. **What does the @app.post decorator do?**

   Answer: It tells FastAPI to route HTTP POST requests to a specific path to the decorated function. The function becomes the handler for that endpoint.

2. **Why do we need CORS middleware?**

   Answer: Browsers block cross-origin requests by default. CORS middleware adds headers that tell browsers "it's OK for this origin to call my API."

3. **What is the difference between /docs and /redoc?**

   Answer: Both show API documentation generated from the OpenAPI spec. /docs is Swagger UI (interactive, can test endpoints). /redoc is ReDoc (cleaner layout, read-only).

4. **Why use environment variables for ALLOWED_ORIGINS?**

   Answer: So we can change the allowed origins without changing code. Development uses localhost, production uses the real frontend URL.

5. **What does response_model=UnfurlResponse do?**

   Answer: It validates that the response matches the schema, documents the response in OpenAPI, and filters out any extra fields not in the model.

6. **Why catch specific exceptions before generic Exception?**

   Answer: To provide specific error messages. "Request timed out" is more helpful than "An error occurred." Python matches the first except block that fits.

7. **What is a health check endpoint used for?**

   Answer: Deployment platforms call it to verify the service is running. If it fails, they may restart the container or stop routing traffic to it.

8. **What does uvicorn --reload do?**

   Answer: Automatically restarts the server when code changes. Essential for development, but should NOT be used in production.

---

## Next Phase

Now that our backend API is complete, we will create the React frontend that calls this API in **Phase 6: React Frontend Setup**.
