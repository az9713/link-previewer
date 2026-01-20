import { useState } from 'react'
import './App.css'

/**
 * Main App component for the Link Previewer
 *
 * This component:
 * 1. Provides a form for users to enter URLs
 * 2. Calls the backend API to extract metadata
 * 3. Displays the preview card with title, description, image
 * 4. Handles loading and error states
 */
function App() {
  // State for the URL input field
  const [url, setUrl] = useState('')

  // State for the API response data
  const [preview, setPreview] = useState(null)

  // State for loading indicator
  const [loading, setLoading] = useState(false)

  // State for error messages
  const [error, setError] = useState(null)

  /**
   * Handle form submission
   * Calls the backend API and updates state based on response
   */
  const handleSubmit = async (e) => {
    // Prevent default form submission (page reload)
    e.preventDefault()

    // Don't submit if URL is empty
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    // Reset state before new request
    setLoading(true)
    setError(null)
    setPreview(null)

    try {
      // Determine API URL based on environment
      // In development, Vite proxy handles /api routes
      // In production, use the environment variable
      const apiUrl = import.meta.env.VITE_API_URL || '/api'

      // Make the API request
      const response = await fetch(`${apiUrl}/unfurl`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      // Parse the JSON response
      const data = await response.json()

      // Check if the API returned an error
      if (!response.ok) {
        // Handle validation errors (422)
        if (data.detail) {
          const errorMsg = Array.isArray(data.detail)
            ? data.detail[0]?.msg || 'Validation error'
            : data.detail
          throw new Error(errorMsg)
        }
        throw new Error('Failed to fetch preview')
      }

      // Check if the unfurl operation succeeded
      if (data.success) {
        setPreview(data.data)
      } else {
        setError(data.error || 'Failed to extract metadata')
      }
    } catch (err) {
      // Handle network errors or other exceptions
      setError(err.message || 'An error occurred')
    } finally {
      // Always stop loading, whether success or failure
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
        {/* URL Input Form */}
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
            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Preview'}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Fetching preview...</p>
          </div>
        )}

        {/* Preview Card */}
        {preview && !loading && (
          <div className="preview-card">
            {/* Preview Image */}
            {preview.image && (
              <div className="preview-image">
                <img
                  src={preview.image}
                  alt={preview.title || 'Preview'}
                  onError={(e) => {
                    // Hide image if it fails to load
                    e.target.style.display = 'none'
                  }}
                />
              </div>
            )}

            {/* Preview Content */}
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
                target="_blank"
                rel="noopener noreferrer"
                className="preview-url"
              >
                {preview.url}
              </a>
            </div>
          </div>
        )}

        {/* Raw JSON Output (for debugging) */}
        {preview && !loading && (
          <details className="json-output">
            <summary>View Raw JSON</summary>
            <pre>{JSON.stringify(preview, null, 2)}</pre>
          </details>
        )}
      </main>

      <footer className="footer">
        <p>
          Built with FastAPI + React |
          <a href="/api/docs" target="_blank" rel="noopener noreferrer"> API Docs</a>
        </p>
      </footer>
    </div>
  )
}

export default App
