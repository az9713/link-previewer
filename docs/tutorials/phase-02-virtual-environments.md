# Phase 2: Virtual Environments and Dependencies - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- What a virtual environment is and why it is essential
- How Python finds and loads packages
- How pip and requirements.txt work together
- What each dependency in our project does
- How to manage project dependencies professionally

---

## 1. The Dependency Problem

### What Are Dependencies?

A **dependency** is code written by someone else that your code relies on. Instead of writing everything from scratch, you use libraries:

```python
# Without dependencies - you write EVERYTHING yourself
def make_http_request(url):
    # 500 lines of socket programming
    # Handle DNS resolution
    # Handle TCP connections
    # Handle HTTP protocol
    # Handle SSL/TLS encryption
    # Handle redirects
    # Handle timeouts
    # Handle errors
    pass

# With dependencies - use someone else's tested code
import httpx
response = httpx.get(url)  # One line!
```

Dependencies save thousands of hours of work.

### The Dependency Hell Problem

Imagine two Python projects on your computer:

**Project A** (built in 2020):
```python
import requests  # Needs version 2.22.0
# Uses old API: requests.get(url, verify=False)
```

**Project B** (built in 2024):
```python
import requests  # Needs version 2.31.0
# Uses new API: requests.get(url, verify=True)  # default changed!
```

**Without virtual environments:**

```
Your Computer
└── Python/
    └── site-packages/
        └── requests/  # Only ONE version can exist!
```

- Install requests 2.22.0 → Project A works, Project B breaks
- Install requests 2.31.0 → Project B works, Project A breaks
- You cannot run both projects!

This is called **dependency hell**.

### Real-World Horror Stories

1. **The Breaking Update**
   - Developer installs new package for Project B
   - New package requires updated requests
   - pip updates requests globally
   - Project A (which was working fine) suddenly crashes
   - Developer spends hours figuring out what broke

2. **The Deployment Disaster**
   - Code works on developer's laptop
   - Code fails on server
   - Reason: Different package versions
   - "But it works on my machine!" - famous last words

3. **The Collaboration Chaos**
   - Alice: "The code works for me"
   - Bob: "It crashes for me"
   - Reason: Alice has requests 2.22, Bob has requests 2.31
   - Hours wasted debugging version differences

---

## 2. Virtual Environments: The Solution

### What is a Virtual Environment?

A **virtual environment** is an isolated Python installation for a single project. Each project gets its own:

- Python interpreter (or a link to one)
- pip package manager
- site-packages folder (where libraries install)

```
Your Computer
├── Project_A/
│   └── venv/
│       └── Lib/site-packages/
│           └── requests 2.22.0  ← Project A's version
│
├── Project_B/
│   └── venv/
│       └── Lib/site-packages/
│           └── requests 2.31.0  ← Project B's version
│
└── Python/  (system Python - don't touch!)
```

Now both projects can coexist peacefully!

### How Virtual Environments Work

When you create a virtual environment:

```bash
python -m venv venv
```

Python creates this structure:

```
venv/
├── Scripts/           # Windows (or bin/ on Mac/Linux)
│   ├── python.exe     # Python interpreter for THIS project
│   ├── pip.exe        # pip for THIS project
│   ├── activate       # Script to "enter" this environment
│   └── deactivate     # Script to "exit" this environment
│
├── Lib/
│   └── site-packages/ # Where YOUR packages install
│       └── (empty initially)
│
├── Include/           # C header files (for compiling extensions)
│
└── pyvenv.cfg         # Configuration file
```

The key insight: `venv/Scripts/python.exe` is configured to look for packages in `venv/Lib/site-packages/` instead of the global location.

### Activating vs Not Activating

**Without activation** (explicit path):
```bash
venv/Scripts/pip install requests
venv/Scripts/python my_script.py
```

**With activation** (convenient):
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Now these commands use the venv automatically:
pip install requests    # Uses venv's pip
python my_script.py     # Uses venv's python
```

When activated, your terminal prompt changes:
```
(venv) C:\Users\simon\project>
```

The `(venv)` prefix reminds you that you are in a virtual environment.

### Creating Our Virtual Environment

```bash
cd backend
python -m venv venv
```

Let us break this down:
- `python` - Use the Python interpreter
- `-m venv` - Run the "venv" module (built into Python 3.3+)
- `venv` - Name of the folder to create

You can name it anything (`python -m venv myenv`), but `venv` is the convention.

---

## 3. Understanding pip and Package Management

### What is pip?

**pip** stands for "Pip Installs Packages" (a recursive acronym). It is Python's package manager:

```bash
pip install requests     # Install a package
pip uninstall requests   # Remove a package
pip list                 # Show installed packages
pip show requests        # Show package details
pip freeze               # Show packages in requirements format
```

### Where Do Packages Come From?

**PyPI** (Python Package Index) at https://pypi.org is the official repository:

```
pypi.org/
├── requests/          # 50+ million downloads/month
├── fastapi/           # Popular web framework
├── numpy/             # Scientific computing
├── django/            # Web framework
└── ... 400,000+ packages
```

When you run `pip install requests`, pip:
1. Connects to PyPI
2. Finds the "requests" package
3. Downloads the latest version (or specified version)
4. Installs it to site-packages
5. Also installs any dependencies that requests needs

### Version Specifiers

You can control which version pip installs:

```bash
pip install requests          # Latest version
pip install requests==2.31.0  # Exactly this version
pip install requests>=2.25.0  # This version or newer
pip install requests<3.0.0    # Older than 3.0.0
pip install requests>=2.25,<3.0  # Range
pip install requests~=2.31.0  # Compatible release (>=2.31.0, <2.32.0)
```

**Why specify versions?**
- Reproducibility: Same version = same behavior
- Stability: New versions might break your code
- Compatibility: Some packages need specific versions of others

### requirements.txt: The Dependency Manifest

A `requirements.txt` file lists all packages your project needs:

```
# requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
httpx>=0.28.0
beautifulsoup4>=4.12.0
pydantic>=2.10.0
lxml>=5.3.0
```

**Why requirements.txt?**

1. **Reproducibility**: Anyone can recreate your environment
   ```bash
   pip install -r requirements.txt  # Installs everything listed
   ```

2. **Documentation**: Shows what your project depends on

3. **Deployment**: Servers use this to install dependencies

4. **Collaboration**: Team members get the same packages

### Creating requirements.txt

**Method 1: Write manually** (what we did)
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
```

**Method 2: Freeze current environment**
```bash
pip freeze > requirements.txt
```

This outputs EXACT versions:
```
annotated-types==0.7.0
anyio==4.12.1
beautifulsoup4==4.14.3
certifi==2026.1.4
...
```

**Which method to use?**
- Manual: More control, only direct dependencies
- Freeze: Exact reproducibility, but includes transitive dependencies

### Transitive Dependencies

When you install `fastapi`, it automatically installs packages that fastapi needs:

```
You install:        fastapi
                       │
                       ├── starlette (fastapi needs this)
                       │      └── anyio (starlette needs this)
                       │             └── idna (anyio needs this)
                       │
                       └── pydantic (fastapi needs this)
                              └── pydantic-core (pydantic needs this)
```

These are **transitive dependencies** - you did not ask for them, but they came along.

`pip freeze` shows ALL of these. Manual requirements.txt shows only what YOU asked for.

---

## 4. Our Dependencies Explained

Let us understand each package we are installing:

### FastAPI - The Web Framework

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

**What it does:**
- Handles HTTP requests (GET, POST, PUT, DELETE)
- Routes URLs to functions (`/unfurl` → `unfurl()`)
- Validates input data automatically
- Generates API documentation
- Handles errors gracefully

**Why FastAPI over alternatives?**

| Framework | Speed | Validation | Docs | Async |
|-----------|-------|------------|------|-------|
| FastAPI | Fast | Built-in | Auto | Yes |
| Flask | Medium | Manual | Manual | No* |
| Django | Slower | Manual | Needs setup | No* |

FastAPI is modern, fast, and does validation for free.

### Uvicorn - The ASGI Server

```bash
uvicorn app.main:app --reload
```

**What it does:**
- Actually runs your FastAPI application
- Listens on a port (default 8000)
- Receives HTTP requests from the internet
- Passes them to FastAPI
- Sends responses back

**Why do we need a separate server?**

FastAPI is the application (your code). Uvicorn is the server (handles networking).

```
Internet Request → Uvicorn (server) → FastAPI (app) → Your Code
                                                           │
Internet Response ← Uvicorn (server) ← FastAPI (app) ← Response
```

Think of it like:
- FastAPI = The chef (cooks the food)
- Uvicorn = The restaurant (handles customers)

**What is [standard]?**

```
uvicorn[standard]>=0.32.0
```

The `[standard]` is an "extra" - optional additional packages:
- `uvloop` - Faster event loop
- `httptools` - Faster HTTP parsing
- `watchfiles` - Auto-reload when code changes
- `websockets` - WebSocket support

### httpx - The HTTP Client

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("https://example.com")
    html = response.text
```

**What it does:**
- Makes HTTP requests to other websites
- We use it to fetch the URLs we want to preview
- Supports async/await (non-blocking)

**Why httpx over requests?**

| Feature | httpx | requests |
|---------|-------|----------|
| Async support | Yes | No |
| HTTP/2 | Yes | No |
| Timeouts | Better API | Confusing |
| Modern | Yes | Older |

Since FastAPI is async, we want an async HTTP client.

### BeautifulSoup4 - The HTML Parser

```python
from bs4 import BeautifulSoup

html = "<html><head><title>Hello</title></head></html>"
soup = BeautifulSoup(html, "lxml")
title = soup.find("title").text  # "Hello"
```

**What it does:**
- Parses HTML into a navigable tree
- Finds elements by tag, class, ID, attributes
- Extracts text and attributes
- Handles malformed HTML gracefully

**Why we need it:**
When we fetch a URL, we get raw HTML. BeautifulSoup lets us find:
- `<title>` tag
- `<meta property="og:title">` tag
- `<meta property="og:image">` tag
- Any other metadata

### Pydantic - Data Validation

```python
from pydantic import BaseModel, HttpUrl

class UnfurlRequest(BaseModel):
    url: HttpUrl

# Automatic validation:
req = UnfurlRequest(url="https://example.com")  # Works
req = UnfurlRequest(url="not-a-url")  # Raises ValidationError
```

**What it does:**
- Defines data schemas (what fields, what types)
- Validates input data automatically
- Converts types (string "123" → int 123)
- Generates JSON schemas

**Why Pydantic matters:**

Without Pydantic:
```python
def unfurl(data):
    if not isinstance(data, dict):
        return {"error": "Expected dict"}
    url = data.get("url")
    if not url:
        return {"error": "url required"}
    if not isinstance(url, str):
        return {"error": "url must be string"}
    if not url.startswith(("http://", "https://")):
        return {"error": "url must be http(s)"}
    # ... 20 more lines
```

With Pydantic:
```python
class UnfurlRequest(BaseModel):
    url: HttpUrl

def unfurl(request: UnfurlRequest):
    # If we get here, request.url is GUARANTEED valid
    pass
```

Pydantic does all that validation automatically.

### lxml - Fast HTML/XML Parser

```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")  # Uses lxml as parser
```

**What it does:**
- Parses HTML/XML very quickly
- Written in C for speed
- BeautifulSoup uses it as a backend

**Why lxml?**

BeautifulSoup can use different parsers:

| Parser | Speed | Lenient | Install |
|--------|-------|---------|---------|
| html.parser | Slow | Medium | Built-in |
| lxml | Fast | Yes | pip install |
| html5lib | Slowest | Very | pip install |

lxml is the best balance of speed and reliability.

---

## 5. The Package Installation Process

Let us trace what happens when we run:

```bash
pip install -r requirements.txt
```

### Step 1: Read requirements.txt

pip reads each line:
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
...
```

### Step 2: Resolve Dependencies

For each package, pip:
1. Contacts PyPI
2. Finds versions matching the specifier (>=0.115.0)
3. Gets the latest matching version
4. Reads THAT package's dependencies
5. Recursively resolves all dependencies

This creates a **dependency tree**:
```
fastapi 0.115.0
├── starlette >=0.40.0
│   └── anyio >=3.6.2
│       ├── idna >=2.8
│       └── sniffio >=1.1
└── pydantic >=2.0.0
    ├── pydantic-core >=2.14.0
    └── annotated-types >=0.4.0
```

### Step 3: Download Packages

pip downloads "wheel" files (.whl) - pre-built packages:
```
Downloading fastapi-0.115.0-py3-none-any.whl (93 kB)
Downloading starlette-0.40.0-py3-none-any.whl (71 kB)
```

Wheel files are ZIP archives containing:
- Python code
- Metadata
- Pre-compiled C extensions (if any)

### Step 4: Install Packages

pip extracts wheels to site-packages:
```
venv/Lib/site-packages/
├── fastapi/
│   ├── __init__.py
│   ├── applications.py
│   └── ...
├── starlette/
└── ...
```

### Step 5: Verify Installation

```bash
pip list
```
Shows all installed packages:
```
Package         Version
--------------- --------
fastapi         0.115.0
starlette       0.40.0
pydantic        2.10.0
...
```

---

## 6. Common Issues and Solutions

### Issue: "pip is not recognized"

**Problem**: System does not know where pip is.

**Solution**: Use `python -m pip` instead:
```bash
python -m pip install requests
```

### Issue: Permission Denied

**Problem**: Trying to install to system Python without admin rights.

**Solution**: Use a virtual environment! That is YOUR folder.

### Issue: Package Requires Compilation

**Problem**: Some packages have C code that needs compiling.

```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solutions**:
1. Install Visual C++ Build Tools (Windows)
2. Use a newer version with pre-built wheels
3. Use `--only-binary :all:` flag

### Issue: Conflicting Dependencies

**Problem**: Package A needs requests>=2.0, Package B needs requests<2.0

```
ERROR: Cannot install A and B because these package versions have conflicting dependencies.
```

**Solutions**:
1. Update packages (newer versions might fix it)
2. Find alternative packages
3. Pin to a version that works for both

### Issue: SSL Certificate Errors

**Problem**: Corporate firewalls interfere with HTTPS.

```
SSLError: certificate verify failed
```

**Solutions**:
1. Install corporate certificates
2. (Not recommended) `pip install --trusted-host pypi.org package`

---

## 7. Best Practices

### Always Use Virtual Environments

```bash
# Good
cd project
python -m venv venv
venv/Scripts/pip install package

# Bad - installs globally!
pip install package
```

### Keep requirements.txt Updated

When you add a new package:
```bash
pip install new-package
# Then add to requirements.txt manually or:
pip freeze > requirements.txt
```

### Use Version Specifiers

```
# Good - predictable
fastapi>=0.115.0,<1.0.0

# Risky - might get breaking changes
fastapi
```

### Separate Dev Dependencies

```
# requirements.txt - production
fastapi>=0.115.0
uvicorn>=0.32.0

# requirements-dev.txt - development only
pytest>=7.0.0
black>=23.0.0
mypy>=1.0.0
```

Install for development:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Document Your Setup

In README.md:
```markdown
## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate it:
   ```bash
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
```

---

## 8. Commands Reference

### Virtual Environment Commands

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Deactivate (any platform)
deactivate

# Delete virtual environment (just delete the folder)
rm -rf venv    # Mac/Linux
rmdir /s venv  # Windows
```

### pip Commands

```bash
# Install single package
pip install requests

# Install specific version
pip install requests==2.31.0

# Install from requirements.txt
pip install -r requirements.txt

# Upgrade package
pip install --upgrade requests

# Uninstall package
pip uninstall requests

# List installed packages
pip list

# Show package info
pip show requests

# Export installed packages
pip freeze > requirements.txt

# Check for outdated packages
pip list --outdated

# Upgrade pip itself
python -m pip install --upgrade pip
```

---

## 9. Self-Check Questions

1. **Why can't two projects share the same requests version?**

   Answer: They might need different versions. requests 2.22 has different behavior than 2.31. One project's code might rely on old behavior, another on new behavior.

2. **What does `pip install -r requirements.txt` do?**

   Answer: Reads each line from requirements.txt and installs that package with pip. It is equivalent to running `pip install X` for each line.

3. **Why use `>=0.115.0` instead of `==0.115.0`?**

   Answer: `>=` allows newer versions with bug fixes and improvements. `==` locks to exactly one version, which might have known bugs. However, `==` guarantees reproducibility.

4. **What is the difference between pip install and pip freeze?**

   Answer: `pip install` adds packages. `pip freeze` outputs a list of installed packages in requirements.txt format (for saving/sharing).

5. **Why do we need both FastAPI AND uvicorn?**

   Answer: FastAPI is the application framework (defines routes, handles logic). Uvicorn is the server (listens on ports, handles network connections). The server runs the application.

6. **What happens if you do not activate the virtual environment?**

   Answer: You can still use it by specifying full paths (`venv/Scripts/pip`). Activation just adds venv to PATH so `pip` and `python` automatically use the venv versions.

7. **What are transitive dependencies?**

   Answer: Dependencies of your dependencies. When you install fastapi, it installs starlette (fastapi needs it), which installs anyio (starlette needs it), etc.

8. **Why is lxml faster than html.parser?**

   Answer: lxml is written in C and compiled to machine code. html.parser is pure Python. C code runs much faster than interpreted Python.

---

## Next Phase

Now that you understand virtual environments and dependencies, we will create the Pydantic data models that define our API's input and output in **Phase 3: Data Models**.
