# Phase 7: Building UI Components - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- React state management with useState
- Handling user input and form submissions
- Making API calls with fetch
- Conditional rendering patterns
- Managing loading and error states
- CSS styling strategies for React
- Responsive design basics

---

## 1. React State Management

### What is State?

State is data that can change over time and affects what the component renders. When state changes, React re-renders the component.

```jsx
import { useState } from 'react'

function Counter() {
  // Declare state: [currentValue, setterFunction] = useState(initialValue)
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

### How useState Works

```jsx
const [value, setValue] = useState(initialValue)
```

- `value` - Current state value
- `setValue` - Function to update state
- `initialValue` - Starting value (only used on first render)

**Important rules:**
1. Always call hooks at the top level (not inside conditions or loops)
2. Only call hooks in React components or custom hooks
3. State updates are asynchronous (batched for performance)

### Our Component's State

```jsx
function App() {
  // Input field value
  const [url, setUrl] = useState('')

  // API response data
  const [preview, setPreview] = useState(null)

  // Loading indicator
  const [loading, setLoading] = useState(false)

  // Error message
  const [error, setError] = useState(null)
```

Each piece of state serves a specific purpose:

| State | Purpose | Initial Value |
|-------|---------|---------------|
| `url` | What the user typed | `''` (empty string) |
| `preview` | Data from API | `null` (no data yet) |
| `loading` | Show loading spinner | `false` |
| `error` | Error message | `null` (no error) |

---

## 2. Handling User Input

### Controlled Components

In React, form inputs can be "controlled" - React manages their value:

```jsx
function Form() {
  const [name, setName] = useState('')

  return (
    <input
      type="text"
      value={name}                          // React controls the value
      onChange={(e) => setName(e.target.value)}  // Update on every keystroke
    />
  )
}
```

**Why controlled?**
- Single source of truth (state)
- Easy to validate/modify input
- Easy to reset or set programmatically

### Our URL Input

```jsx
<input
  type="text"
  value={url}                              // Controlled by url state
  onChange={(e) => setUrl(e.target.value)} // Update state on change
  placeholder="https://example.com"        // Hint text
  className="url-input"                    // CSS class
  disabled={loading}                       // Disable during loading
/>
```

### The onChange Event

When the user types, `onChange` fires with an event object:

```jsx
onChange={(e) => {
  console.log(e.target)        // The input element
  console.log(e.target.value)  // Current input value
  setUrl(e.target.value)       // Update state
}}
```

---

## 3. Form Submission

### Preventing Default Behavior

HTML forms submit to the server and reload the page. We want JavaScript to handle it:

```jsx
const handleSubmit = (e) => {
  e.preventDefault()  // Stop form from submitting normally
  // Handle submission with JavaScript
}

return (
  <form onSubmit={handleSubmit}>
    <input type="text" />
    <button type="submit">Submit</button>
  </form>
)
```

### Our Submit Handler

```jsx
const handleSubmit = async (e) => {
  // 1. Prevent page reload
  e.preventDefault()

  // 2. Validate input
  if (!url.trim()) {
    setError('Please enter a URL')
    return
  }

  // 3. Reset state for new request
  setLoading(true)
  setError(null)
  setPreview(null)

  try {
    // 4. Make API call
    const response = await fetch('/api/unfurl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.trim() }),
    })

    // 5. Parse response
    const data = await response.json()

    // 6. Handle result
    if (data.success) {
      setPreview(data.data)
    } else {
      setError(data.error)
    }
  } catch (err) {
    // 7. Handle network errors
    setError(err.message)
  } finally {
    // 8. Always stop loading
    setLoading(false)
  }
}
```

### The async/await Pattern

```jsx
// async function can use await
const handleSubmit = async (e) => {
  // await pauses until Promise resolves
  const response = await fetch(url)
  const data = await response.json()
}
```

This is cleaner than Promise chains:

```jsx
// Equivalent with .then()
fetch(url)
  .then(response => response.json())
  .then(data => { /* use data */ })
  .catch(err => { /* handle error */ })
```

---

## 4. Making API Calls with Fetch

### The Fetch API

`fetch()` is the browser's built-in way to make HTTP requests:

```jsx
// GET request
const response = await fetch('https://api.example.com/data')

// POST request with JSON body
const response = await fetch('https://api.example.com/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ key: 'value' }),
})

// Read response
const data = await response.json()  // Parse as JSON
const text = await response.text()  // Parse as text
```

### Our API Call

```jsx
const apiUrl = import.meta.env.VITE_API_URL || '/api'

const response = await fetch(`${apiUrl}/unfurl`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ url: url.trim() }),
})
```

**Breaking it down:**
- `import.meta.env.VITE_API_URL` - Environment variable for production
- `'/api'` - Fallback for development (Vite proxy)
- `method: 'POST'` - HTTP method
- `headers` - Tell server we're sending JSON
- `body: JSON.stringify(...)` - Convert JS object to JSON string

### Handling the Response

```jsx
const data = await response.json()

// Check HTTP status
if (!response.ok) {
  // response.ok is false for 4xx and 5xx
  throw new Error('Request failed')
}

// Check our API's success flag
if (data.success) {
  setPreview(data.data)
} else {
  setError(data.error)
}
```

### Environment Variables in Vite

Vite exposes env vars starting with `VITE_`:

```bash
# .env file
VITE_API_URL=https://api.example.com
```

```jsx
// In code
const apiUrl = import.meta.env.VITE_API_URL
```

**Important:** These are baked in at build time, not runtime!

---

## 5. Conditional Rendering

### Showing/Hiding Elements

React offers several ways to conditionally render:

**1. && operator (show if true)**
```jsx
{isLoggedIn && <LogoutButton />}
// If isLoggedIn is true, render LogoutButton
// If false, render nothing
```

**2. Ternary operator (either/or)**
```jsx
{isLoggedIn ? <LogoutButton /> : <LoginButton />}
// If true, render LogoutButton
// If false, render LoginButton
```

**3. Early return**
```jsx
function Component({ data }) {
  if (!data) {
    return <p>No data</p>
  }
  return <DataDisplay data={data} />
}
```

### Our Conditional Rendering

```jsx
{/* Show error if exists */}
{error && (
  <div className="error-message">
    {error}
  </div>
)}

{/* Show loading spinner */}
{loading && (
  <div className="loading">
    <div className="spinner"></div>
  </div>
)}

{/* Show preview card if data exists and not loading */}
{preview && !loading && (
  <div className="preview-card">
    {/* Card content */}
  </div>
)}
```

### Rendering Lists

When rendering arrays, each item needs a unique `key`:

```jsx
{items.map(item => (
  <li key={item.id}>{item.name}</li>
))}
```

**Why keys?**
- Help React identify which items changed
- Enable efficient updates
- Must be unique among siblings

---

## 6. Component Structure

### Our App Component Structure

```
App
├── Header
│   ├── h1 (title)
│   └── p (subtitle)
├── Main
│   ├── Form
│   │   └── Input Group
│   │       ├── URL Input
│   │       └── Submit Button
│   ├── Error Message (conditional)
│   ├── Loading Indicator (conditional)
│   ├── Preview Card (conditional)
│   │   ├── Preview Image
│   │   └── Preview Content
│   │       ├── Site Name
│   │       ├── Title
│   │       ├── Description
│   │       └── URL Link
│   └── JSON Output (conditional)
└── Footer
```

### The Preview Card

```jsx
{preview && !loading && (
  <div className="preview-card">
    {/* Image - only if exists */}
    {preview.image && (
      <div className="preview-image">
        <img
          src={preview.image}
          alt={preview.title || 'Preview'}
          onError={(e) => {
            // Hide if image fails to load
            e.target.style.display = 'none'
          }}
        />
      </div>
    )}

    {/* Content */}
    <div className="preview-content">
      {preview.site_name && (
        <span className="site-name">{preview.site_name}</span>
      )}

      {preview.title && (
        <h2 className="preview-title">{preview.title}</h2>
      )}

      {preview.description && (
        <p className="preview-description">{preview.description}</p>
      )}

      <a
        href={preview.url}
        target="_blank"           // Open in new tab
        rel="noopener noreferrer" // Security: prevent tab-nabbing
        className="preview-url"
      >
        {preview.url}
      </a>
    </div>
  </div>
)}
```

### Handling Image Errors

Images might fail to load (404, CORS, etc.). We handle this gracefully:

```jsx
<img
  src={preview.image}
  onError={(e) => {
    e.target.style.display = 'none'  // Hide broken image
  }}
/>
```

---

## 7. CSS Styling Strategies

### CSS Files (Our Approach)

Each component imports its own CSS file:

```jsx
import './App.css'
```

**Pros:**
- Simple and familiar
- No build-time processing
- Full CSS features

**Cons:**
- Global scope (class names can conflict)
- No dynamic styles

### CSS Class Naming

We use descriptive, specific class names:

```css
.preview-card { }      /* Component name */
.preview-image { }     /* Sub-element */
.preview-title { }     /* Sub-element */
.preview-url { }       /* Sub-element */
```

This is similar to BEM (Block Element Modifier) methodology.

### Key CSS Concepts Used

**Flexbox for layout:**
```css
.input-group {
  display: flex;      /* Enable flexbox */
  gap: 0.5rem;        /* Space between items */
}

.url-input {
  flex: 1;            /* Take remaining space */
}
```

**CSS Transitions for polish:**
```css
.submit-button {
  transition: background-color 0.2s, transform 0.1s;
}

.submit-button:hover {
  background-color: #535bf2;
}

.submit-button:active {
  transform: scale(0.98);
}
```

**CSS Animations:**
```css
.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

---

## 8. Responsive Design

### Mobile-First Approach

Write base styles for mobile, then add breakpoints for larger screens:

```css
/* Base styles (mobile) */
.input-group {
  flex-direction: column;  /* Stack vertically */
}

/* Larger screens */
@media (min-width: 600px) {
  .input-group {
    flex-direction: row;   /* Side by side */
  }
}
```

### Our Responsive Styles

```css
/* Mobile: Stack form elements */
@media (max-width: 600px) {
  .app {
    padding: 1rem;
  }

  .header h1 {
    font-size: 2rem;
  }

  .input-group {
    flex-direction: column;
  }

  .submit-button {
    width: 100%;
  }

  .preview-title {
    font-size: 1.25rem;
  }
}
```

### Viewport Meta Tag

In `index.html`:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

This ensures proper scaling on mobile devices.

---

## 9. Dark Mode Support

### CSS Media Query

```css
@media (prefers-color-scheme: dark) {
  .app {
    background-color: #1a1a2e;
  }

  .header h1 {
    color: #ffffff;
  }

  .preview-card {
    background-color: #2d2d44;
    border-color: #404060;
  }
}
```

### How It Works

1. User's OS has light/dark mode setting
2. Browser exposes this via `prefers-color-scheme`
3. CSS automatically applies matching styles

### CSS Variables for Theming

```css
:root {
  --bg-color: #f5f5f7;
  --text-color: #1a1a2e;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #1a1a2e;
    --text-color: #ffffff;
  }
}

body {
  background-color: var(--bg-color);
  color: var(--text-color);
}
```

---

## 10. Error Handling Best Practices

### Types of Errors

1. **Validation errors** - User input is invalid
2. **Network errors** - Can't reach server
3. **API errors** - Server returned an error
4. **Unexpected errors** - Bugs, edge cases

### Our Error Handling

```jsx
try {
  const response = await fetch(...)
  const data = await response.json()

  // HTTP error (4xx, 5xx)
  if (!response.ok) {
    if (data.detail) {
      // FastAPI validation error format
      const msg = data.detail[0]?.msg || 'Validation error'
      throw new Error(msg)
    }
    throw new Error('Request failed')
  }

  // API-level error
  if (!data.success) {
    setError(data.error || 'Failed to extract metadata')
    return
  }

  // Success
  setPreview(data.data)

} catch (err) {
  // Network error or thrown error
  setError(err.message || 'An error occurred')
} finally {
  // Always runs
  setLoading(false)
}
```

### User-Friendly Error Messages

```jsx
{error && (
  <div className="error-message">
    <span className="error-icon">⚠️</span>
    {error}
  </div>
)}
```

Style errors to be noticeable but not alarming.

---

## 11. The Complete App.jsx

```jsx
import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setLoading(true)
    setError(null)
    setPreview(null)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api'
      const response = await fetch(`${apiUrl}/unfurl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail?.[0]?.msg || 'Request failed')
      }

      if (data.success) {
        setPreview(data.data)
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Link Previewer</h1>
        <p>Enter a URL to extract its metadata</p>
      </header>

      <main className="main">
        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="url-input"
              disabled={loading}
            />
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Loading...' : 'Preview'}
            </button>
          </div>
        </form>

        {error && <div className="error-message">⚠️ {error}</div>}
        {loading && <div className="loading"><div className="spinner" /></div>}
        {preview && !loading && (
          <div className="preview-card">
            {/* Preview content */}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
```

---

## 12. Commands Reference

### React Hooks

```jsx
// State
const [value, setValue] = useState(initialValue)

// Effect (side effects)
useEffect(() => {
  // Run on mount and when deps change
  return () => { /* cleanup */ }
}, [dependencies])

// Context
const value = useContext(MyContext)

// Ref (DOM access)
const inputRef = useRef(null)
```

### Fetch API

```jsx
// GET
const response = await fetch(url)

// POST with JSON
const response = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
})

// Read response
const json = await response.json()
const text = await response.text()

// Check status
response.ok      // true for 200-299
response.status  // 200, 404, 500, etc.
```

### Event Handlers

```jsx
// Form events
onSubmit={(e) => { e.preventDefault(); }}
onChange={(e) => setValue(e.target.value)}

// Mouse events
onClick={() => { }}
onMouseEnter={() => { }}

// Image events
onError={(e) => { e.target.style.display = 'none' }}
onLoad={() => { }}
```

---

## 13. Self-Check Questions

1. **Why do we call e.preventDefault() in handleSubmit?**

   Answer: To prevent the default form submission behavior, which would cause a page reload. We want JavaScript to handle the submission instead.

2. **What is a controlled component?**

   Answer: A form element whose value is controlled by React state. The input's value comes from state, and onChange updates state. React is the "single source of truth."

3. **Why use useState for loading and error states?**

   Answer: So the UI can react to changes. When loading becomes true, React re-renders to show the spinner. When error changes, the error message appears.

4. **What does `{preview && <Card />}` do?**

   Answer: Conditional rendering. If preview is truthy (not null/undefined), render the Card. If preview is null, render nothing.

5. **Why set loading to true before the API call?**

   Answer: To show the loading spinner immediately while waiting for the response. Users see feedback that something is happening.

6. **What is the purpose of the finally block?**

   Answer: Code that runs whether the try succeeded or catch caught an error. We use it to ensure loading is set to false regardless of outcome.

7. **Why use CSS variables for theming?**

   Answer: They can be changed in one place (the :root) and affect everywhere they're used. This makes dark mode simple - just change variable values.

8. **What does `rel="noopener noreferrer"` do on links?**

   Answer: Security measure for links with `target="_blank"`. Prevents the new page from accessing window.opener, which could be used for phishing attacks.

---

## Next Phase

Now that we have the UI built, we need to test everything working together in **Phase 8: Local Integration Testing**.
