# Phase 1: Project Structure Setup - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- Why software projects need organized folder structures
- The difference between monorepos and polyrepos
- How Git version control works and why it matters
- What .gitignore does and why it is critical for security
- How to think about separating concerns in a full-stack application

---

## 1. Why Project Structure Matters

### The Problem with No Structure

Imagine you are building a house and you throw all your materials in one pile: nails mixed with lumber, electrical wire tangled with plumbing pipes, blueprints buried under drywall. You could build the house, but:

- Finding anything takes forever
- You might accidentally use the wrong materials
- No one else could help you because they cannot find anything
- Coming back after a week, you have forgotten where everything is

Software projects have the same problem. Without structure:

```
my_project/
├── app.py
├── index.html
├── styles.css
├── database.py
├── Button.jsx
├── test_app.py
├── config.json
├── utils.py
├── package.json
├── requirements.txt
└── ... 50 more files
```

This becomes unmaintainable quickly. Where is the frontend code? Where is the backend? Where are the tests?

### The Solution: Intentional Organization

A well-structured project tells a story:

```
link-previewer/
├── backend/           # All server-side code lives here
│   ├── app/           # The actual Python application
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── models.py
│   ├── tests/         # Backend tests
│   └── requirements.txt
├── frontend/          # All client-side code lives here
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── docs/              # Documentation and tutorials
```

Now anyone can instantly understand:
- Backend problems? Look in backend/
- Frontend bugs? Check frontend/
- Need to add a Python package? Edit backend/requirements.txt

---

## 2. Monorepo vs Polyrepo: A Critical Decision

### What is a Repository?

A **repository** (repo) is a folder tracked by Git. It contains:
- Your code
- The complete history of every change ever made
- Information about who made each change and why

Think of it like a folder with a time machine built in. You can go back to any point in history and see exactly what the code looked like.

### Polyrepo: Separate Repositories

In a **polyrepo** setup, each component gets its own Git repository:

```
github.com/you/link-previewer-backend   # One repo
github.com/you/link-previewer-frontend  # Another repo
```

**Advantages:**
- Clear separation of concerns
- Teams can work independently
- Each repo can have different access permissions
- Smaller repos are faster to clone
- Can use different CI/CD pipelines

**Disadvantages:**
- Coordinating changes is hard (API change requires two separate PRs)
- Version synchronization is manual ("Which frontend version works with which backend?")
- More repositories to manage
- Harder to run the full system locally
- Shared code requires publishing packages

**When to use polyrepo:**
- Large organizations with separate teams
- Components that are truly independent
- Open source projects where parts have different licenses
- When you need different access controls

### Monorepo: One Repository

In a **monorepo** setup, everything lives together:

```
github.com/you/link-previewer/
├── backend/
├── frontend/
├── shared/          # Code used by both
└── docs/
```

**Advantages:**
- Atomic changes (one commit can update API + UI together)
- Easier to run locally (just clone once)
- Shared tooling and configuration
- Easier to understand the full system
- Refactoring across boundaries is simple
- Single source of truth

**Disadvantages:**
- Repository can get large over time
- Everyone has access to everything (may not want this)
- CI/CD needs to be smart about what changed
- Git operations slow down with huge repos

**When to use monorepo:**
- Small to medium teams
- Tightly coupled components
- Rapid development where API and UI change together
- When you want simple local development

### Our Choice: Monorepo

For this project, a monorepo makes sense because:
- We are one developer (or small team)
- Frontend and backend are tightly coupled (frontend calls backend API)
- We want simple local development (one clone, one place)
- Deployment coordination is easier (one repo = one deployment pipeline)

---

## 3. Understanding Separation of Concerns

### What Are "Concerns"?

A "concern" is a distinct aspect or responsibility of your application. Think of it like roles in a restaurant:

| Restaurant Role | Software Concern |
|-----------------|------------------|
| Chef (cooking) | Business logic |
| Waiter (customer interface) | User interface |
| Host (receiving guests) | HTTP handling |
| Quality control | Data validation |
| Supplier relations | External API calls |

Each role has a specific responsibility. The chef does not take orders from customers, and the waiter does not cook food. This separation makes the restaurant run smoothly.

### Software Concerns in Our Project

| Concern | Responsibility | Our File |
|---------|----------------|----------|
| HTTP handling | Receive requests, send responses | main.py |
| Data validation | Ensure inputs are correct | models.py |
| URL fetching | Get content from external URLs | unfurl.py |
| HTML parsing | Extract metadata from HTML | unfurl.py |
| User interface | Display results to user | App.jsx |
| Styling | How the UI looks | index.css |

### Why Separate Them?

**Without separation** (everything in one file):

```python
# app.py - 2000 lines of everything mixed together
from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/unfurl", methods=["POST"])
def unfurl():
    # Validate input (lines 1-50)
    data = request.get_json()
    if not data:
        return {"error": "No JSON"}, 400
    url = data.get("url")
    if not url:
        return {"error": "No URL"}, 400
    if not url.startswith("http"):
        return {"error": "Invalid URL"}, 400
    # ... more validation

    # Fetch URL (lines 51-150)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        return {"error": "Timeout"}, 504
    except requests.RequestException as e:
        return {"error": str(e)}, 502

    # Parse HTML (lines 151-300)
    soup = BeautifulSoup(response.text, "html.parser")
    title = None
    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content")
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text
    # ... 100 more lines of parsing

    # Format response (lines 301-400)
    # Handle errors (scattered everywhere)
    pass
```

**Problems with this approach:**
1. **Hard to test**: How do you test just the HTML parsing without making HTTP requests?
2. **Hard to read**: 2000 lines is overwhelming
3. **Hard to change**: Fixing a parsing bug might accidentally break validation
4. **Hard to reuse**: Cannot use the parsing logic in another project
5. **Hard to collaborate**: Two developers cannot work on parsing and validation simultaneously

**With separation**:

```
backend/app/
├── main.py      # HTTP handling only (50 lines)
├── models.py    # Data validation only (30 lines)
├── unfurl.py    # Fetching + parsing only (100 lines)
└── utils.py     # Shared helpers (20 lines)
```

**Benefits:**
1. **Easy to test**: Test parsing with fake HTML, no network needed
2. **Easy to read**: Each file has one job, fits on one screen
3. **Easy to change**: Changes are localized
4. **Easy to reuse**: Import unfurl.py in another project
5. **Easy to collaborate**: Work on different files simultaneously

### The Single Responsibility Principle

This separation follows the **Single Responsibility Principle (SRP)**:

> A module should have one, and only one, reason to change.

- `models.py` changes when the API contract changes
- `unfurl.py` changes when parsing logic changes
- `main.py` changes when endpoints change

If one file has multiple reasons to change, it is doing too much.

### Frontend vs Backend: The Ultimate Separation

**Backend** (runs on server):
- Executes on your server (Railway, AWS, etc.)
- Has access to secrets (database passwords, API keys)
- Can make server-to-server requests
- Handles data processing and storage
- Written in Python, Node.js, Go, Java, etc.
- User never sees this code

**Frontend** (runs in browser):
- Executes on user's computer (their browser)
- Has NO access to secrets (anyone can view source)
- Can only make requests to URLs
- Handles display and user interaction
- Written in JavaScript, HTML, CSS
- User can inspect all of this code

**Why they MUST be separate:**

1. **Different execution environments**: Server vs browser
2. **Different security contexts**: Secrets vs public
3. **Different deployment**: Server process vs static files
4. **Different languages**: Python vs JavaScript
5. **Different update cycles**: Backend can update without users refreshing

**The communication pattern:**

```
User's Browser                         Your Server
┌─────────────┐                       ┌─────────────┐
│  Frontend   │  ──HTTP Request──>    │  Backend    │
│  (React)    │                       │  (FastAPI)  │
│             │  <──JSON Response──   │             │
└─────────────┘                       └─────────────┘
```

The frontend makes HTTP requests to the backend API. The backend processes the request and returns JSON data. They communicate through a well-defined interface (the API).

---

## 4. Git Version Control Deep Dive

### What is Git?

Git is a **distributed version control system**. Let us break that down:

- **Version**: A snapshot of your code at a point in time
- **Control**: Ability to manage, compare, and restore versions
- **System**: Software that does this automatically
- **Distributed**: Every copy is a complete backup

### The Problem Git Solves

**Before version control** (how people used to work):

```
project_v1/
project_v2/
project_v2_fixed/
project_v2_fixed_FINAL/
project_v2_fixed_FINAL_really/
project_v2_fixed_FINAL_really_v2/
project_backup_jan15/
project_old_dont_delete/
```

Problems:
- Which version is current? Nobody knows.
- What changed between v1 and v2? Have to manually compare.
- How do you merge two people's changes? Copy and paste carefully.
- How do you undo a bad change? Hope you have a backup.
- Who made this change and why? No record exists.

**With Git**:

```
project/
├── .git/           # Git stores ALL history here
│   ├── objects/    # Every version of every file, compressed
│   ├── refs/       # Pointers to commits (branches, tags)
│   └── HEAD        # Current position in history
├── main.py
└── utils.py
```

Git remembers:
- Every change ever made (even deleted files)
- Who made each change (author)
- When it was made (timestamp)
- Why it was made (commit message)
- How to undo any change (revert)

### Key Git Concepts Explained

#### Repository (Repo)

A folder tracked by Git. Created with `git init` or `git clone`.

```bash
git init                    # Creates .git/ folder, starts tracking
git clone <url>             # Copies a remote repo to your machine
```

The `.git/` folder IS the repository. Everything else is your "working directory."

#### Commit

A snapshot of your code at a specific moment. Like a save point in a video game.

```
commit a1b2c3d4e5f6...
Author: Jane Developer <jane@example.com>
Date:   Mon Jan 20 2025 10:30:00

    Add user authentication

    - Created login endpoint
    - Added password hashing with bcrypt
    - Set up JWT token generation
    - Added tests for auth flow
```

Each commit has:
- **Hash**: Unique identifier (a1b2c3d4...)
- **Author**: Who made the change
- **Date**: When it was made
- **Message**: Why it was made
- **Parent(s)**: What commit(s) came before it
- **Changes**: What files were modified

#### Staging Area (Index)

A holding area for changes you want to commit. Think of it as a shopping cart.

```bash
# Working directory → Staging area → Repository

git add file.py        # Add specific file to staging
git add .              # Add all changes to staging
git status             # See what is staged vs not staged
git commit -m "msg"    # Commit everything in staging
```

Why have staging? It lets you commit related changes together:

```bash
# You fixed a bug AND added a feature
git add bugfix.py
git commit -m "Fix login timeout bug"

git add feature.py new_tests.py
git commit -m "Add password reset feature"
```

Two separate, logical commits instead of one messy one.

#### Branch

A parallel line of development. The default branch is usually called `main` or `master`.

```
main:     A───B───C───────────G───H
               \             /
feature:        D───E───F───┘
```

- You start on main at commit C
- Create a branch called "feature"
- Make commits D, E, F on the feature branch
- Merge feature back into main (creates G)
- Continue on main (H)

Why branch?
- Work on features without affecting main
- Multiple people can work on different features
- Easy to abandon failed experiments
- Keep main stable while developing

```bash
git branch feature      # Create branch
git checkout feature    # Switch to branch
git checkout -b feature # Create AND switch (shortcut)
git merge feature       # Merge feature into current branch
```

#### Remote

A copy of the repository on a server (GitHub, GitLab, Bitbucket).

```bash
git remote add origin https://github.com/you/project.git
git push origin main    # Upload your commits to remote
git pull origin main    # Download commits from remote
git fetch origin        # Download without merging
```

Remotes enable:
- Backup (code is not just on your laptop)
- Collaboration (others can clone and contribute)
- Deployment (servers can pull latest code)

### Initializing a Repository

```bash
git init
```

This creates the `.git/` folder structure:

```
.git/
├── HEAD              # Points to current branch (ref: refs/heads/main)
├── config            # Repository settings
├── description       # Used by GitWeb (rarely)
├── hooks/            # Scripts that run on events
├── info/
│   └── exclude       # Like .gitignore but not shared
├── objects/          # Git's database (empty initially)
│   ├── info/
│   └── pack/
└── refs/
    ├── heads/        # Branch pointers
    └── tags/         # Tag pointers
```

After `git init`, Git is watching but has not saved anything. You need to:

```bash
git add .                    # Stage all files
git commit -m "Initial commit"  # Save first snapshot
```

### Common Git Workflow

```bash
# 1. Check status (what changed?)
git status

# 2. See the changes
git diff

# 3. Stage changes
git add .

# 4. Commit with a message
git commit -m "Add feature X"

# 5. Push to remote
git push origin main
```

---

## 5. The .gitignore File: Security and Cleanliness

### What is .gitignore?

A `.gitignore` file tells Git: "Pretend these files do not exist. Never track them."

```gitignore
# This is a comment

# Ignore all .log files
*.log

# Ignore the node_modules folder
node_modules/

# Ignore this specific file
.env

# Ignore all files in build/ except keep.txt
build/*
!build/keep.txt
```

### Why is .gitignore Critical?

#### 1. Security: Protecting Secrets

```
# .env file - NEVER commit this!
DATABASE_URL=postgresql://user:password123@db.example.com/mydb
API_KEY=sk-abc123xyz789
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=sk_live_abc123
```

**If you commit .env:**
- Anyone who clones the repo sees your passwords
- Hackers actively scan GitHub for accidentally committed secrets
- Bots find exposed AWS keys within minutes and spin up crypto miners
- Git history is permanent - even if you delete the file, the commit exists
- You would have to rotate EVERY secret immediately

**Real-world examples:**
- Company leaked AWS keys, got a $14,000 bill overnight from crypto mining
- Startup exposed database credentials, had all user data stolen
- Developer committed API key, had it used for spam within hours

#### 2. Cleanliness: Avoiding Generated Files

These files should never be committed because they are **generated** and can be recreated:

| File/Folder | Size | Why It Exists | Why Ignore It |
|-------------|------|---------------|---------------|
| `node_modules/` | 100MB+ | npm packages | Regenerated by `npm install` |
| `venv/` | 50MB+ | Python virtual env | Regenerated by `python -m venv` |
| `__pycache__/` | Variable | Python bytecode | Auto-created when Python runs |
| `dist/` | Variable | Build output | Regenerated by build command |
| `.pyc` files | Small | Compiled Python | Auto-created when importing |

**Problems with committing generated files:**
- Repository becomes huge (node_modules can be 500MB+)
- Constant merge conflicts (these files change frequently)
- Slower clone times
- Wastes storage on GitHub

#### 3. Avoiding Platform-Specific Files

These files are created by your operating system or IDE:

| File | Created By | Why Ignore |
|------|------------|------------|
| `.DS_Store` | macOS | Folder metadata |
| `Thumbs.db` | Windows | Image thumbnails |
| `.idea/` | JetBrains IDEs | Project settings |
| `.vscode/` | VS Code | Workspace settings |
| `*.swp` | Vim | Swap files |

**Problems:**
- Every developer has different OS/IDE settings
- Constant merge conflicts
- Personal preferences leak into repo

### Glob Patterns in .gitignore

.gitignore uses "glob" patterns for matching files:

| Pattern | What It Matches | Example Matches |
|---------|-----------------|-----------------|
| `*.log` | Any file ending in .log | error.log, debug.log |
| `logs/` | Directory named logs | logs/app.log, logs/error.log |
| `/logs/` | logs/ in root only | logs/ but not src/logs/ |
| `*.py[cod]` | .pyc, .pyo, or .pyd | cache.pyc, module.pyo |
| `**/*.tmp` | .tmp anywhere | a.tmp, dir/b.tmp, deep/dir/c.tmp |
| `!important.log` | Exception: DO track | important.log is tracked |
| `build/*` | Everything in build/ | build/output.js |
| `doc/*.txt` | .txt files in doc/ | doc/readme.txt |

### Our .gitignore Explained

```gitignore
# ========== Python ==========
# Python compiles .py files to bytecode for faster execution
# These are auto-generated and machine-specific
__pycache__/          # Bytecode cache folder
*.py[cod]             # Compiled Python files (.pyc, .pyo, .pyd)
*$py.class            # Jython compiled files
*.so                  # Compiled C extensions

# Virtual environment - contains Python interpreter and all packages
# Machine-specific (Windows vs Mac vs Linux have different binaries)
venv/
ENV/
env/
.venv/

# ========== Node.js ==========
# npm packages - can be 100MB+, regenerated by npm install
node_modules/

# Debug logs from npm operations
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# ========== Build Outputs ==========
# These are generated by build commands, not source code
dist/                 # Webpack/Vite production build
build/                # Generic build output
*.egg-info/           # Python package metadata

# ========== Secrets & Environment ==========
# NEVER commit these - they contain passwords and API keys
.env                  # Environment variables
.env.local            # Local environment overrides
.env.*.local          # Environment-specific files

# ========== IDE & Editor ==========
# Personal preferences, cause merge conflicts
.idea/                # JetBrains (PyCharm, WebStorm)
.vscode/              # Visual Studio Code
*.swp                 # Vim swap files
*.swo                 # Vim swap files
*~                    # Backup files from various editors

# ========== Operating System ==========
# OS-specific files that leak personal info
.DS_Store             # macOS folder attributes
Thumbs.db             # Windows thumbnail cache

# ========== Testing ==========
# Test output and coverage reports
.coverage             # Coverage.py data file
htmlcov/              # Coverage HTML report
.pytest_cache/        # Pytest cache
```

### What If I Already Committed a Secret?

If you accidentally committed a secret:

1. **Immediately rotate the secret** (change password, regenerate API key)
2. Add the file to .gitignore
3. Remove from Git tracking: `git rm --cached .env`
4. Commit the removal
5. Consider using `git filter-branch` or BFG Repo-Cleaner to remove from history

**Warning**: Even after removal, the commit still exists. Anyone who cloned before your fix has the secret. Always rotate compromised secrets.

---

## 6. Putting It All Together

### Our Complete Project Structure

```
link-previewer/
│
├── .git/                    # Git's database (auto-created by git init)
│   └── ...                  # All version history lives here
│
├── .gitignore               # Files Git should ignore
│
├── backend/                 # ══════ Python/FastAPI Server ══════
│   │
│   ├── app/                 # Python package (the actual application)
│   │   ├── __init__.py      # Makes this folder a Python package
│   │   ├── main.py          # FastAPI app, routes, HTTP handling
│   │   ├── models.py        # Pydantic models for validation
│   │   └── unfurl.py        # URL fetching and HTML parsing logic
│   │
│   ├── venv/                # Virtual environment (gitignored)
│   │   ├── Scripts/         # Python executables (Windows)
│   │   └── Lib/             # Installed packages
│   │
│   ├── requirements.txt     # Python dependencies list
│   └── Procfile             # Deployment instructions for Railway
│
├── frontend/                # ══════ React/Vite Client ══════
│   │
│   ├── src/                 # Source code
│   │   ├── App.jsx          # Main React component
│   │   ├── main.jsx         # Application entry point
│   │   └── index.css        # Styles
│   │
│   ├── node_modules/        # npm packages (gitignored)
│   ├── index.html           # HTML template
│   ├── package.json         # npm dependencies and scripts
│   └── vite.config.js       # Vite bundler configuration
│
└── docs/                    # ══════ Documentation ══════
    └── tutorials/           # Learning materials (these files)
        ├── phase-01-project-structure.md
        ├── phase-02-virtual-environments.md
        └── phase-03-data-models.md
```

### Understanding __init__.py

In Python, a folder is just a folder. To make it a **package** (something you can import from), it needs an `__init__.py` file:

```
backend/app/              # Just a folder, cannot import
backend/app/__init__.py   # Now it's a package!
```

**Without __init__.py:**
```python
from app.models import UnfurlRequest
# ModuleNotFoundError: No module named 'app'
```

**With __init__.py:**
```python
from app.models import UnfurlRequest  # Works!
from app.unfurl import extract_metadata  # Works!
```

The `__init__.py` file can be completely empty. Its mere presence tells Python "this folder is a package." However, you can also use it to:

```python
# __init__.py
from .models import UnfurlRequest, UnfurlResponse
from .unfurl import extract_metadata

# Now users can do:
# from app import UnfurlRequest
# Instead of:
# from app.models import UnfurlRequest
```

---

## 7. Commands Reference

### Directory Commands

```bash
# Create a directory
mkdir backend

# Create nested directories (-p = create parents if needed)
mkdir -p backend/app frontend/src docs/tutorials

# List directory contents
ls              # Basic list
ls -la          # Detailed list with hidden files
dir             # Windows equivalent

# Change directory
cd backend      # Go into backend folder
cd ..           # Go up one level
cd ~            # Go to home directory
```

### Git Commands

```bash
# Initialize a new repository
git init

# Check repository status
git status

# Stage files for commit
git add file.py           # Add specific file
git add .                 # Add all changes
git add *.py              # Add all Python files

# Commit staged changes
git commit -m "Your message here"

# View commit history
git log                   # Full history
git log --oneline         # Compact view

# View changes
git diff                  # Unstaged changes
git diff --staged         # Staged changes

# Create and switch branches
git branch feature        # Create branch
git checkout feature      # Switch to branch
git checkout -b feature   # Create and switch (shortcut)

# Connect to remote
git remote add origin https://github.com/user/repo.git
git push -u origin main   # Push and set upstream
git pull origin main      # Pull latest changes
```

### File Commands

```bash
# Create empty file
touch file.py             # Unix/Mac/Git Bash
type nul > file.py        # Windows CMD

# View file contents
cat file.py               # Unix/Mac/Git Bash
type file.py              # Windows CMD

# Copy files
cp source.py dest.py      # Unix/Mac
copy source.py dest.py    # Windows

# Move/rename files
mv old.py new.py          # Unix/Mac
move old.py new.py        # Windows

# Delete files
rm file.py                # Unix/Mac
del file.py               # Windows
```

---

## 8. Self-Check Questions

Test your understanding:

1. **Why don't we commit node_modules/?**

   Answer: It is huge (often 100MB+), machine-specific (different binaries for Windows/Mac/Linux), and can be perfectly recreated by running `npm install` using package.json.

2. **What would happen if we committed .env with our database password?**

   Answer: Anyone who clones the repo would see the password. Even if we delete the file later, it remains in Git history forever. Hackers actively scan GitHub for leaked secrets. We would need to immediately change the password.

3. **Why is backend/app/ a separate folder from backend/?**

   Answer: `app/` is a Python package (can be imported), while `backend/` is just an organizational folder that also contains configuration files like requirements.txt and Procfile that are not part of the Python code.

4. **What's the difference between a monorepo and polyrepo?**

   Answer: Monorepo keeps all code (frontend, backend, shared) in one repository, making atomic changes easy but the repo larger. Polyrepo uses separate repositories for each component, giving better isolation but making coordination harder.

5. **Why do we need __init__.py?**

   Answer: It tells Python "this folder is a package that can be imported." Without it, you cannot do `from app.models import ...`. The file can be empty; its presence is what matters.

6. **What does `git add .` do?**

   Answer: Stages ALL changes in the current directory (and subdirectories) for the next commit. The changes move from "working directory" to "staging area."

7. **Why use a staging area instead of committing directly?**

   Answer: It lets you group related changes into logical commits. You might fix a bug AND add a feature, but want them as separate commits for clearer history.

8. **What happens if you run `git init` in a folder that is already a Git repo?**

   Answer: Git will reinitialize the repository, which is mostly harmless. It will say "Reinitialized existing Git repository." Your history and commits are preserved.

---

## Next Phase

Now that you understand project structure, version control, and why we organize code this way, we will set up the Python virtual environment and install dependencies in **Phase 2: Virtual Environments and Dependencies**.
