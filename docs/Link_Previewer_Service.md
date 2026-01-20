# Link Previewer / URL Unfurler Service

A microservice that extracts metadata from URLs to generate link preview cards.

---

## What This Service Does

When you paste a link in Slack, Discord, or Twitter - you see a preview card appear. This service provides the data for that card.

```
┌─────────────────────────────────────────────┐
│  User pastes: https://github.com/nodejs     │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  [Preview Image]                    │   │
│  │                                     │   │
│  │ Node.js                             │   │
│  │ Node.js JavaScript runtime          │   │
│  │ github.com                          │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ^ This card is built from unfurl data      │
└─────────────────────────────────────────────┘
```

---

## Input & Output

### Input (What the user/developer sends)

Just a URL:

```json
{
  "url": "https://github.com/nodejs/node"
}
```

That's it. One field.

### Output (What the service returns)

The metadata extracted from that webpage:

```json
{
  "success": true,
  "data": {
    "url": "https://github.com/nodejs/node",
    "title": "GitHub - nodejs/node: Node.js JavaScript runtime",
    "description": "Node.js JavaScript runtime. Contribute to nodejs/node development by creating an account on GitHub.",
    "image": "https://opengraph.githubassets.com/abc123/nodejs/node",
    "site_name": "GitHub",
    "type": "website",
    "favicon": "https://github.githubassets.com/favicons/favicon.svg"
  }
}
```

---

## Real Examples

### Example 1: YouTube Video

**Input:**
```json
{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
```

**Output:**
```json
{
  "success": true,
  "data": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "description": "The official video for Rick Astley's \"Never Gonna Give You Up\"",
    "image": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "site_name": "YouTube",
    "type": "video"
  }
}
```

### Example 2: News Article

**Input:**
```json
{"url": "https://techcrunch.com/some-article"}
```

**Output:**
```json
{
  "success": true,
  "data": {
    "url": "https://techcrunch.com/some-article",
    "title": "Some Tech Company Raises $50M",
    "description": "The startup announced a Series B round...",
    "image": "https://techcrunch.com/wp-content/uploads/article-image.jpg",
    "site_name": "TechCrunch",
    "type": "article",
    "author": "John Smith",
    "published_time": "2026-01-15T10:30:00Z"
  }
}
```

### Example 3: Invalid URL

**Input:**
```json
{"url": "https://this-site-does-not-exist-12345.com"}
```

**Output:**
```json
{
  "success": false,
  "error": {
    "code": "FETCH_FAILED",
    "message": "Could not reach the URL"
  }
}
```

---

## Who Uses This & How

| User Type | How They Use It |
|-----------|-----------------|
| **Chat app developer** | When user pastes link, call this API to show preview |
| **CMS/Blog platform** | Auto-generate link cards in posts |
| **Social media tool** | Preview links before posting |
| **Bookmark manager** | Auto-fill title/description when saving link |

---

## Architecture Flow

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│              │         │                  │         │              │
│  Your App    │─────►   │  Link Previewer  │─────►   │  Target URL  │
│  (Client)    │         │  (Your Service)  │         │  (Any site)  │
│              │◄─────   │                  │◄─────   │              │
└──────────────┘         └──────────────────┘         └──────────────┘
     │                          │                           │
     │ Sends URL                │ Fetches page              │ Returns HTML
     │                          │ Parses metadata           │
     │ Receives JSON            │ Returns structured data   │
```

---

## API Specification

### Endpoint

```
POST /unfurl
```

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "url": "https://example.com/page"
}
```

### Response (Success)

**Status:** `200 OK`

```json
{
  "success": true,
  "data": {
    "url": "https://example.com/page",
    "title": "Page Title",
    "description": "Page description text",
    "image": "https://example.com/og-image.jpg",
    "site_name": "Example",
    "type": "website",
    "favicon": "https://example.com/favicon.ico"
  }
}
```

### Response (Error)

**Status:** `200 OK` (with error in body) or `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "FETCH_FAILED",
    "message": "Could not reach the URL"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_URL` | The provided URL is malformed |
| `FETCH_FAILED` | Could not connect to the URL |
| `TIMEOUT` | Request took too long |
| `NO_METADATA` | Page exists but has no extractable metadata |

---

## Optional: Simple Frontend

A demo web page where users can test the service:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Link Previewer                                    │
│                                                     │
│   ┌─────────────────────────────────────┐  ┌─────┐ │
│   │ https://example.com/article         │  │ Go  │ │
│   └─────────────────────────────────────┘  └─────┘ │
│                                                     │
│   Preview:                                          │
│   ┌─────────────────────────────────────────────┐  │
│   │ [Image]                                     │  │
│   │ Example Article Title                       │  │
│   │ This is the description of the article...   │  │
│   │ example.com                                 │  │
│   └─────────────────────────────────────────────┘  │
│                                                     │
│   JSON Response:                                    │
│   {"title": "Example Article Title", ...}          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## How It Works (Technical)

The service extracts metadata from HTML pages using:

1. **Open Graph tags** (Facebook standard, widely adopted)
   ```html
   <meta property="og:title" content="Page Title">
   <meta property="og:description" content="Description">
   <meta property="og:image" content="https://example.com/image.jpg">
   ```

2. **Twitter Card tags** (fallback)
   ```html
   <meta name="twitter:title" content="Page Title">
   <meta name="twitter:description" content="Description">
   ```

3. **Standard HTML tags** (final fallback)
   ```html
   <title>Page Title</title>
   <meta name="description" content="Description">
   ```

---

## Tech Stack (Planned)

| Component | Technology |
|-----------|------------|
| Backend | Python + FastAPI |
| HTML Parsing | BeautifulSoup or lxml |
| HTTP Client | httpx (async) |
| Frontend | React + Vite |
| Deployment | Railway (backend) + Vercel (frontend) |

---

*Document created: January 2026*
