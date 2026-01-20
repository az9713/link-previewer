# Phase 6: React Frontend Setup - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- What React is and why it's popular
- What Vite is and how it improves development
- How modern JavaScript projects are structured
- What JSX is and how it works
- How npm and package.json manage dependencies
- How to configure development proxies
- The difference between development and production builds

---

## 1. What is React?

### Overview

React is a JavaScript library for building user interfaces. Created by Facebook in 2013, it's now the most popular frontend framework.

### Why React?

**1. Component-Based Architecture**
Instead of building pages, you build components (reusable pieces):

```jsx
// A reusable Button component
function Button({ text, onClick }) {
  return <button onClick={onClick}>{text}</button>;
}

// Use it anywhere
<Button text="Click me" onClick={handleClick} />
<Button text="Submit" onClick={handleSubmit} />
```

**2. Declarative UI**
You describe WHAT you want, not HOW to do it:

```jsx
// Declarative (React) - describe the result
function UserList({ users }) {
  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}

// vs Imperative (vanilla JS) - describe steps
function renderUserList(users) {
  const ul = document.createElement('ul');
  for (const user of users) {
    const li = document.createElement('li');
    li.textContent = user.name;
    ul.appendChild(li);
  }
  document.body.appendChild(ul);
}
```

**3. Virtual DOM**
React tracks changes efficiently:
- You update state
- React calculates minimal DOM changes
- Only changed elements are updated

This is faster than rebuilding the entire page.

**4. Rich Ecosystem**
- Huge community
- Thousands of libraries
- Excellent documentation
- Many job opportunities

### React vs Other Frameworks

| Feature | React | Vue | Angular |
|---------|-------|-----|---------|
| Learning Curve | Medium | Easy | Steep |
| Size | Medium | Small | Large |
| Flexibility | High | Medium | Low |
| Corporate Backing | Meta | Independent | Google |
| Popularity | Highest | High | Medium |

React is the most popular choice, especially for complex applications.

---

## 2. What is Vite?

### The Problem with Traditional Bundlers

Old tools like Webpack:
1. Bundle ALL your code before starting dev server
2. Re-bundle on every change
3. Slow startup (30+ seconds for large projects)
4. Slow hot reload (2-5 seconds)

### Vite's Solution

Vite (French for "fast") uses a different approach:

**Development:**
- Uses native ES modules (no bundling needed)
- Only processes files when requested
- Instant server start
- Instant hot reload

**Production:**
- Uses Rollup for optimized bundling
- Tree shaking (removes unused code)
- Code splitting (loads only what's needed)

### Speed Comparison

| Operation | Webpack | Vite |
|-----------|---------|------|
| Cold Start | 30-60s | <1s |
| Hot Reload | 2-5s | <100ms |
| Build | Similar | Similar |

### How Vite Works

```
Development Mode:
Browser requests main.jsx
  → Vite transforms JSX to JS on-the-fly
  → Browser executes native ES modules
  → No bundling needed!

Production Mode:
vite build
  → Rollup bundles everything
  → Optimized, minified output
  → Ready for deployment
```

---

## 3. Project Structure

### Files Created by Vite

```
frontend/
├── node_modules/        # Installed packages (gitignored)
├── public/              # Static files (copied as-is)
│   └── vite.svg         # Favicon
├── src/                 # Source code
│   ├── assets/          # Images, fonts, etc.
│   │   └── react.svg
│   ├── App.css          # Component styles
│   ├── App.jsx          # Main component
│   ├── index.css        # Global styles
│   └── main.jsx         # Entry point
├── .gitignore           # Git ignore patterns
├── eslint.config.js     # Linting configuration
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── package-lock.json    # Locked versions
└── vite.config.js       # Vite configuration
```

### Key Files Explained

**index.html** - The HTML template
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Note: `<script type="module">` - This enables ES modules in the browser.

**main.jsx** - Entry point
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

This:
1. Imports React and your App component
2. Finds the `<div id="root">` element
3. Renders your App inside it

**App.jsx** - Main component
```jsx
import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1>Vite + React</h1>
      <button onClick={() => setCount(count + 1)}>
        count is {count}
      </button>
    </>
  )
}

export default App
```

---

## 4. Understanding JSX

### What is JSX?

JSX (JavaScript XML) lets you write HTML-like code in JavaScript:

```jsx
// JSX
const element = <h1>Hello, World!</h1>;

// Gets compiled to:
const element = React.createElement('h1', null, 'Hello, World!');
```

JSX is NOT HTML. It's syntactic sugar that compiles to JavaScript function calls.

### JSX Rules

**1. Must have one root element**
```jsx
// WRONG - multiple roots
return (
  <h1>Title</h1>
  <p>Paragraph</p>
);

// RIGHT - single root
return (
  <div>
    <h1>Title</h1>
    <p>Paragraph</p>
  </div>
);

// RIGHT - Fragment (no extra DOM element)
return (
  <>
    <h1>Title</h1>
    <p>Paragraph</p>
  </>
);
```

**2. Close all tags**
```jsx
// HTML allows this
<input type="text">
<br>
<img src="pic.jpg">

// JSX requires closing
<input type="text" />
<br />
<img src="pic.jpg" />
```

**3. Use className instead of class**
```jsx
// HTML
<div class="container">

// JSX (class is reserved in JavaScript)
<div className="container">
```

**4. Use camelCase for attributes**
```jsx
// HTML
<button onclick="handleClick()" tabindex="1">

// JSX
<button onClick={handleClick} tabIndex={1}>
```

**5. JavaScript expressions in curly braces**
```jsx
const name = "Alice";
const items = ['a', 'b', 'c'];

return (
  <div>
    {/* Variables */}
    <h1>Hello, {name}!</h1>

    {/* Expressions */}
    <p>2 + 2 = {2 + 2}</p>

    {/* Conditional rendering */}
    {isLoggedIn && <p>Welcome back!</p>}
    {isLoggedIn ? <LogoutButton /> : <LoginButton />}

    {/* Lists */}
    <ul>
      {items.map(item => <li key={item}>{item}</li>)}
    </ul>
  </div>
);
```

---

## 5. npm and package.json

### What is npm?

npm (Node Package Manager) is JavaScript's package manager, like pip for Python.

```bash
npm install           # Install all dependencies
npm install react     # Install a package
npm uninstall react   # Remove a package
npm run dev           # Run a script
npm run build         # Build for production
```

### package.json Explained

```json
{
  "name": "frontend",           // Project name
  "private": true,              // Don't publish to npm
  "version": "0.0.0",           // Project version
  "type": "module",             // Use ES modules

  "scripts": {
    "dev": "vite",              // npm run dev
    "build": "vite build",      // npm run build
    "preview": "vite preview",  // npm run preview
    "lint": "eslint ."          // npm run lint
  },

  "dependencies": {
    "react": "^19.0.0",         // Runtime dependencies
    "react-dom": "^19.0.0"      // (included in build)
  },

  "devDependencies": {
    "vite": "^6.0.0",           // Development only
    "@vitejs/plugin-react": "^4.0.0"  // (not in build)
  }
}
```

### dependencies vs devDependencies

**dependencies** - Needed at runtime
- react, react-dom
- Included in the production build

**devDependencies** - Needed for development only
- vite, eslint
- NOT included in production build

### Version Specifiers

```json
"react": "^19.0.0"   // ^major.minor.patch
```

| Prefix | Meaning | Example |
|--------|---------|---------|
| `^19.0.0` | Compatible (19.x.x) | 19.0.0, 19.1.0, 19.2.5 |
| `~19.0.0` | Patch only (19.0.x) | 19.0.0, 19.0.1, 19.0.9 |
| `19.0.0` | Exact version | Only 19.0.0 |
| `*` | Any version | Anything |

### package-lock.json

Locks exact versions of ALL packages (including transitive dependencies):

```json
{
  "packages": {
    "node_modules/react": {
      "version": "19.0.0",      // Exact version
      "resolved": "https://...", // Where it came from
      "integrity": "sha512-..."  // Checksum for verification
    }
  }
}
```

This ensures everyone gets the exact same versions.

---

## 6. Vite Configuration

### vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### Understanding the Proxy

Without a proxy, you'd have CORS issues:
```
Frontend (localhost:5173) → Backend (localhost:8000)
Browser blocks this! Different origins!
```

With a proxy:
```
Frontend (localhost:5173) → Vite Proxy → Backend (localhost:8000)
Browser thinks it's same origin!
```

How our proxy works:
```javascript
proxy: {
  '/api': {                              // When URL starts with /api
    target: 'http://localhost:8000',     // Forward to backend
    changeOrigin: true,                  // Change Origin header
    rewrite: (path) => path.replace(/^\/api/, ''),  // Remove /api prefix
  },
}
```

Example:
```
Frontend calls: /api/unfurl
Proxy rewrites to: http://localhost:8000/unfurl
```

### Why Use a Proxy?

1. **Avoids CORS in development** - Same-origin requests work without CORS
2. **Matches production pattern** - Frontend calls /api/..., just like in production
3. **Simple configuration** - One place to configure backend URL

---

## 7. Development vs Production

### Development Mode

```bash
npm run dev
```

- Starts Vite dev server on localhost:5173
- Hot Module Replacement (HMR) - instant updates
- Source maps for debugging
- No optimization (faster rebuilds)
- Proxy enabled

### Production Build

```bash
npm run build
```

Creates `dist/` folder with optimized output:

```
dist/
├── index.html           # Minified HTML
├── assets/
│   ├── index-abc123.js  # Bundled, minified JS
│   └── index-def456.css # Bundled, minified CSS
```

Optimizations:
- **Minification** - Remove whitespace, shorten names
- **Tree shaking** - Remove unused code
- **Code splitting** - Load only what's needed
- **Asset hashing** - Cache busting

### Preview Production Build

```bash
npm run preview
```

Serves the `dist/` folder locally to test the production build.

---

## 8. ES Modules

### What are ES Modules?

ES Modules are JavaScript's official module system (since ES6/2015):

```javascript
// Exporting
export function add(a, b) {
  return a + b;
}

export const PI = 3.14159;

export default function main() {
  // ...
}

// Importing
import main, { add, PI } from './math.js';
```

### CommonJS vs ES Modules

**CommonJS** (Node.js traditional):
```javascript
// Export
module.exports = { add, subtract };

// Import
const { add, subtract } = require('./math');
```

**ES Modules** (modern standard):
```javascript
// Export
export { add, subtract };

// Import
import { add, subtract } from './math.js';
```

Vite uses ES modules because:
- Native browser support (no bundling needed in dev)
- Static analysis (enables tree shaking)
- Standard syntax (works everywhere)

### type: "module" in package.json

```json
{
  "type": "module"
}
```

This tells Node.js to treat `.js` files as ES modules, not CommonJS.

---

## 9. Running the Frontend

### Start Development Server

```bash
cd frontend
npm run dev
```

Output:
```
  VITE v6.0.0  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

### Development Features

**Hot Module Replacement (HMR)**
- Edit a file
- Save
- Browser updates instantly (no refresh needed)
- State is preserved

**Error Overlay**
- Syntax errors shown in browser
- Click to open in editor
- Stack traces with source maps

**Fast Refresh**
- React-specific HMR
- Preserves component state during updates
- Only re-renders changed components

### Build for Production

```bash
npm run build
```

Output:
```
vite v6.0.0 building for production...
✓ 32 modules transformed.
dist/index.html                  0.46 kB
dist/assets/index-abc123.js    142.35 kB │ gzip: 45.67 kB
dist/assets/index-def456.css     1.23 kB │ gzip:  0.52 kB
✓ built in 1.23s
```

### Preview Production Build

```bash
npm run preview
```

Serves dist/ folder on localhost:4173 to test production build.

---

## 10. Commands Reference

### npm Commands

```bash
# Install dependencies from package.json
npm install

# Install a package (add to dependencies)
npm install react

# Install as dev dependency
npm install --save-dev eslint

# Install globally
npm install -g vite

# Remove a package
npm uninstall react

# Run a script from package.json
npm run dev
npm run build

# Update packages
npm update

# Check for outdated packages
npm outdated

# View installed packages
npm list
npm list --depth=0  # Only top-level
```

### Vite Commands

```bash
# Start dev server
npm run dev
# or
npx vite

# Build for production
npm run build
# or
npx vite build

# Preview production build
npm run preview
# or
npx vite preview

# With options
npx vite --port 3000
npx vite --host 0.0.0.0
npx vite build --mode staging
```

### Project Scripts

In package.json:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

Run with: `npm run <script-name>`

---

## 11. Self-Check Questions

1. **What is the difference between React and Vite?**

   Answer: React is a UI library for building components. Vite is a build tool that handles bundling, dev server, and hot reload. They work together - Vite builds React applications.

2. **Why does Vite start faster than Webpack?**

   Answer: Vite uses native ES modules in development - it doesn't bundle your code, just transforms files on-demand. Webpack bundles everything before starting.

3. **What does the proxy configuration do?**

   Answer: It forwards requests from the frontend to the backend during development. `/api/unfurl` on localhost:5173 gets forwarded to `http://localhost:8000/unfurl`, avoiding CORS issues.

4. **What is the difference between dependencies and devDependencies?**

   Answer: dependencies are needed at runtime (included in production build). devDependencies are only needed during development (vite, eslint) and not included in production.

5. **Why must JSX elements have a single root?**

   Answer: JSX compiles to `React.createElement()` calls, which return a single element. Multiple roots would be multiple return values, which JavaScript doesn't support directly.

6. **What does `type: "module"` in package.json do?**

   Answer: Tells Node.js to treat `.js` files as ES modules (import/export) instead of CommonJS (require/module.exports).

7. **What is Hot Module Replacement (HMR)?**

   Answer: A development feature where code changes update in the browser instantly without a full page refresh, preserving application state.

8. **What is tree shaking?**

   Answer: A build optimization that removes unused code. If you import `{ add }` from a file that also exports `subtract`, the `subtract` function is removed from the bundle.

---

## Next Phase

Now that the frontend project is set up, we will build the actual UI components that call our API in **Phase 7: Building the UI Components**.
