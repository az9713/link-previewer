# Phase 4: URL Extraction Logic - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- How to make HTTP requests in Python with httpx
- What async/await means and why it matters for web services
- How HTML pages are structured (DOM tree)
- What Open Graph and Twitter Card meta tags are
- How to parse HTML and extract data with BeautifulSoup
- Error handling patterns for network operations
- The concept of graceful degradation

---

## 1. The Problem: Getting Data from URLs

### What We Need to Do

When a user sends us a URL like `https://github.com`, we need to:

1. **Fetch** the HTML content from that URL
2. **Parse** the HTML to find metadata
3. **Extract** title, description, image, site name
4. **Return** the structured data

This is what happens when you paste a link into Slack, Discord, or Twitter - they "unfurl" the link to show a preview.

### The Challenges

**Network Issues:**
- The URL might not exist (404)
- The server might be slow (timeout)
- The server might block us (403)
- The connection might fail (network error)

**Content Issues:**
- The page might not be HTML (could be PDF, image, JSON)
- The HTML might be malformed
- The page might be huge (memory issues)
- Metadata might be missing

**Security Issues:**
- Malicious URLs trying to exploit our server
- Infinite redirects
- Very slow responses (denial of service)

Our code must handle all of these gracefully.

---

## 2. Making HTTP Requests with httpx

### What is httpx?

httpx is a modern HTTP client for Python. It is like the popular `requests` library, but with async support.

### Synchronous vs Asynchronous

**Synchronous (blocking):**
```python
import requests

# This BLOCKS - Python waits until done
response = requests.get("https://example.com")  # Wait 2 seconds...
print(response.text)  # Now we can continue
```

During those 2 seconds, your server cannot do anything else. If 100 users make requests simultaneously, they wait in line.

**Asynchronous (non-blocking):**
```python
import httpx
import asyncio

async def fetch():
    async with httpx.AsyncClient() as client:
        # This YIELDS - Python can do other work while waiting
        response = await client.get("https://example.com")
        return response.text

asyncio.run(fetch())
```

With async, while waiting for one request, the server can handle other requests. 100 simultaneous users can all be served efficiently.

### The async/await Keywords

**async** - Marks a function as asynchronous (a "coroutine")
```python
async def my_function():
    # This function can use 'await'
    pass
```

**await** - Pauses execution until the awaited operation completes
```python
async def fetch_data():
    response = await client.get(url)  # Pause here, let other code run
    return response.text  # Resume when response arrives
```

Think of it like ordering at a restaurant:
- **Sync**: You stand at the counter waiting until your food is ready
- **Async**: You get a buzzer, sit down, and the buzzer alerts you when food is ready

### Making a Request with httpx

```python
import httpx

async def fetch_url(url: str) -> str:
    # Create an async client (context manager ensures cleanup)
    async with httpx.AsyncClient() as client:
        # Make the GET request
        response = await client.get(
            url,
            timeout=10.0,           # Give up after 10 seconds
            follow_redirects=True,  # Follow 301/302 redirects
            headers={
                "User-Agent": "MyBot/1.0",  # Identify ourselves
            }
        )

        # Check for HTTP errors (4xx, 5xx)
        response.raise_for_status()

        # Return the HTML content
        return response.text
```

### Important Request Options

| Option | Purpose | Example |
|--------|---------|---------|
| `timeout` | Max wait time | `timeout=10.0` |
| `follow_redirects` | Handle 301/302 | `follow_redirects=True` |
| `headers` | Custom HTTP headers | `headers={"User-Agent": "..."}` |
| `params` | Query parameters | `params={"q": "search"}` |
| `auth` | Authentication | `auth=("user", "pass")` |

### Handling HTTP Errors

```python
import httpx

async def safe_fetch(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.text

    except httpx.TimeoutException:
        # Server took too long to respond
        raise ValueError(f"Request timed out: {url}")

    except httpx.HTTPStatusError as e:
        # Server returned 4xx or 5xx
        raise ValueError(f"HTTP error {e.response.status_code}: {url}")

    except httpx.RequestError as e:
        # Network error (DNS failure, connection refused, etc.)
        raise ValueError(f"Request failed: {e}")
```

### HTTP Status Codes You Should Know

| Code | Meaning | How to Handle |
|------|---------|---------------|
| 200 | OK | Success! Process the content |
| 301/302 | Redirect | Follow (httpx does this automatically) |
| 400 | Bad Request | Our request was malformed |
| 403 | Forbidden | Server blocked us |
| 404 | Not Found | URL does not exist |
| 429 | Rate Limited | We're making too many requests |
| 500 | Server Error | Their server has a problem |
| 503 | Unavailable | Server is overloaded |

---

## 3. Understanding HTML Structure

### What is HTML?

HTML (HyperText Markup Language) is how web pages are structured. It is a tree of nested elements:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My Page</title>
    <meta name="description" content="A description">
    <meta property="og:title" content="Open Graph Title">
    <meta property="og:image" content="https://example.com/image.png">
  </head>
  <body>
    <h1>Hello World</h1>
    <p>Some content</p>
  </body>
</html>
```

### The DOM Tree

HTML forms a tree structure called the DOM (Document Object Model):

```
html
├── head
│   ├── title
│   │   └── "My Page"
│   ├── meta (name="description")
│   └── meta (property="og:title")
└── body
    ├── h1
    │   └── "Hello World"
    └── p
        └── "Some content"
```

### Elements We Care About

For link previews, we need to find:

**The `<title>` tag:**
```html
<title>Page Title Here</title>
```

**Meta description:**
```html
<meta name="description" content="Page description here">
```

**Open Graph tags (Facebook's standard):**
```html
<meta property="og:title" content="Title for social media">
<meta property="og:description" content="Description for social media">
<meta property="og:image" content="https://example.com/preview.png">
<meta property="og:site_name" content="Example Site">
```

**Twitter Card tags:**
```html
<meta name="twitter:title" content="Title for Twitter">
<meta name="twitter:description" content="Description for Twitter">
<meta name="twitter:image" content="https://example.com/twitter-card.png">
```

---

## 4. Open Graph Protocol Deep Dive

### What is Open Graph?

Open Graph is a protocol created by Facebook in 2010. It lets websites define how their content appears when shared on social media.

Without Open Graph, Facebook (and other platforms) have to guess what title/image to show. With Open Graph, the website explicitly defines it.

### Why Open Graph Matters

When you share a link on:
- Facebook
- LinkedIn
- Slack
- Discord
- iMessage
- WhatsApp

These platforms look for Open Graph tags to build the preview.

### Common Open Graph Tags

```html
<!-- Required tags -->
<meta property="og:title" content="The Rock">
<meta property="og:type" content="video.movie">
<meta property="og:url" content="https://www.imdb.com/title/tt0117500/">
<meta property="og:image" content="https://example.com/rock.jpg">

<!-- Optional but recommended -->
<meta property="og:description" content="A group of U.S. Marines...">
<meta property="og:site_name" content="IMDb">
<meta property="og:locale" content="en_US">

<!-- Image details -->
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Movie poster for The Rock">
```

### Twitter Cards

Twitter has its own system (Twitter Cards) that works similarly:

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@username">
<meta name="twitter:title" content="Title here">
<meta name="twitter:description" content="Description here">
<meta name="twitter:image" content="https://example.com/image.png">
```

### Our Extraction Priority

We check in this order (first match wins):

1. **Open Graph** - Most widely supported
2. **Twitter Card** - Fallback for Twitter-specific sites
3. **Standard HTML** - Last resort for minimal pages

```python
def extract_title(soup):
    # Try og:title first
    title = get_meta(soup, "og:title")
    if title:
        return title

    # Try twitter:title
    title = get_meta(soup, "twitter:title")
    if title:
        return title

    # Fall back to <title> tag
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.text

    return None
```

---

## 5. Parsing HTML with BeautifulSoup

### What is BeautifulSoup?

BeautifulSoup is a Python library for parsing HTML and XML. It creates a navigable tree from messy HTML and provides methods to find elements.

### Creating a Soup Object

```python
from bs4 import BeautifulSoup

html = """
<html>
  <head><title>Test</title></head>
  <body><p class="content">Hello</p></body>
</html>
"""

# Parse with lxml (fast)
soup = BeautifulSoup(html, "lxml")

# Or parse with built-in parser (no extra install)
soup = BeautifulSoup(html, "html.parser")
```

### Finding Elements

**Find one element:**
```python
# By tag name
title = soup.find("title")
print(title.text)  # "Test"

# By attribute
meta = soup.find("meta", property="og:title")
print(meta["content"])  # Gets the content attribute

# By CSS class
p = soup.find("p", class_="content")
print(p.text)  # "Hello"
```

**Find all matching elements:**
```python
# All paragraph tags
paragraphs = soup.find_all("p")

# All meta tags with property attribute
og_tags = soup.find_all("meta", property=True)
```

### Accessing Element Data

```python
# Given: <meta property="og:title" content="Hello">
meta = soup.find("meta", property="og:title")

# Get attribute value
content = meta["content"]  # "Hello"
content = meta.get("content")  # "Hello" (or None if missing)

# Get tag name
tag_name = meta.name  # "meta"

# Get inner text (for tags with content)
# Given: <title>Page Title</title>
title_tag = soup.find("title")
text = title_tag.text  # "Page Title"
text = title_tag.string  # "Page Title" (only if single text node)
```

### Handling Missing Elements

```python
# WRONG - crashes if element not found
meta = soup.find("meta", property="og:title")
content = meta["content"]  # AttributeError if meta is None!

# RIGHT - check before accessing
meta = soup.find("meta", property="og:title")
if meta and meta.get("content"):
    content = meta["content"]
else:
    content = None

# BETTER - helper function
def get_meta_content(soup, property_name):
    meta = soup.find("meta", property=property_name)
    if meta and meta.get("content"):
        return meta["content"].strip()
    return None
```

### Why lxml vs html.parser?

| Parser | Speed | Lenient | Requires Install |
|--------|-------|---------|------------------|
| lxml | Fast | Yes | Yes (pip install lxml) |
| html.parser | Slow | Medium | No (built-in) |
| html5lib | Slowest | Very | Yes |

We use lxml for speed, with fallback to html.parser:

```python
try:
    soup = BeautifulSoup(html, "lxml")
except:
    soup = BeautifulSoup(html, "html.parser")
```

---

## 6. Our Extraction Implementation

### The Overall Flow

```
URL → fetch_url() → HTML string → parse_html() → UnfurlData
```

### fetch_url() Function

```python
async def fetch_url(url: str) -> str:
    """Fetch HTML content from a URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

        response.raise_for_status()

        # Safety checks
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content too large: {content_length} bytes")

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            raise ValueError(f"Not HTML content: {content_type}")

        return response.text
```

**Key points:**
- Uses async/await for non-blocking I/O
- Sets timeout to prevent hanging
- Follows redirects automatically
- Sends proper headers (some sites block requests without User-Agent)
- Validates content before processing

### extract_meta_tag() Function

```python
def extract_meta_tag(soup: BeautifulSoup, property_name: str) -> Optional[str]:
    """Extract content from a meta tag."""
    # Try property attribute (Open Graph style)
    # <meta property="og:title" content="...">
    tag = soup.find("meta", property=property_name)
    if tag and tag.get("content"):
        return tag["content"].strip()

    # Try name attribute (Twitter/standard style)
    # <meta name="twitter:title" content="...">
    tag = soup.find("meta", attrs={"name": property_name})
    if tag and tag.get("content"):
        return tag["content"].strip()

    return None
```

**Why two lookups?**
- Open Graph uses `property` attribute: `<meta property="og:title">`
- Twitter uses `name` attribute: `<meta name="twitter:title">`
- Standard meta uses `name` attribute: `<meta name="description">`

### Extraction Functions

Each extractor follows the same pattern - try multiple sources with fallback:

```python
def extract_title(soup: BeautifulSoup) -> Optional[str]:
    # Priority 1: Open Graph
    title = extract_meta_tag(soup, "og:title")
    if title:
        return title

    # Priority 2: Twitter
    title = extract_meta_tag(soup, "twitter:title")
    if title:
        return title

    # Priority 3: HTML <title> tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    return None
```

### All Extraction Functions

We have extraction functions for many types of metadata:

| Function | Fields Extracted | Source Tags |
|----------|-----------------|-------------|
| `extract_title()` | title | og:title, twitter:title, `<title>` |
| `extract_description()` | description | og:description, twitter:description, description |
| `extract_image()` | image | og:image, twitter:image |
| `extract_site_name()` | site_name | og:site_name |
| `extract_type()` | type | og:type |
| `extract_locale()` | locale | og:locale |
| `extract_author()` | author | article:author, author |
| `extract_publisher()` | publisher | article:publisher, publisher |
| `extract_published_time()` | published_time | article:published_time, og:published_time, date |
| `extract_modified_time()` | modified_time | article:modified_time, og:updated_time |
| `extract_video_url()` | video_url | og:video:url, og:video, og:video:secure_url |
| `extract_audio_url()` | audio_url | og:audio:url, og:audio |
| `extract_duration()` | duration | og:video:duration, video:duration |
| `extract_twitter_handle()` | twitter_handle | twitter:creator, twitter:site |
| `extract_twitter_card()` | twitter_card | twitter:card |
| `extract_canonical_url()` | canonical_url | `<link rel="canonical">`, og:url |
| `extract_favicon()` | favicon | `<link rel="icon">`, `<link rel="shortcut icon">` |
| `extract_theme_color()` | theme_color | theme-color |
| `extract_keywords()` | keywords | keywords (parsed into list) |

### Handling Relative URLs

URLs for images, videos, and favicons might be relative:

```html
<!-- Absolute URL - ready to use -->
<meta property="og:image" content="https://example.com/image.png">

<!-- Relative URL - needs conversion -->
<meta property="og:image" content="/images/preview.png">
```

We convert relative to absolute using `urljoin`:

```python
from urllib.parse import urljoin

def extract_image(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    image = extract_meta_tag(soup, "og:image")
    if image:
        # urljoin handles both absolute and relative URLs correctly
        return urljoin(base_url, image)
    return None
```

Examples:
```python
urljoin("https://example.com/page", "/images/pic.png")
# → "https://example.com/images/pic.png"

urljoin("https://example.com/page", "https://cdn.example.com/pic.png")
# → "https://cdn.example.com/pic.png" (already absolute, unchanged)

urljoin("https://example.com/blog/post", "../images/pic.png")
# → "https://example.com/images/pic.png"
```

### Parsing Keywords into a List

Keywords are comma-separated in HTML but we want a proper list:

```python
def extract_keywords(soup: BeautifulSoup) -> Optional[List[str]]:
    keywords_str = extract_meta_tag(soup, "keywords")
    if keywords_str:
        # "python, api, tutorial" → ["python", "api", "tutorial"]
        keywords = [k.strip() for k in keywords_str.split(",")]
        keywords = [k for k in keywords if k]  # Remove empty strings
        return keywords if keywords else None
    return None
```

### parse_html() Function

Orchestrates all extraction:

```python
def parse_html(html: str, url: str) -> UnfurlData:
    """Parse HTML and extract all metadata."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    return UnfurlData(
        # Basic metadata
        url=url,
        title=extract_title(soup),
        description=extract_description(soup),
        image=extract_image(soup, url),
        site_name=extract_site_name(soup),

        # Content type
        type=extract_type(soup),
        locale=extract_locale(soup),

        # Authorship
        author=extract_author(soup),
        publisher=extract_publisher(soup),

        # Timestamps
        published_time=extract_published_time(soup),
        modified_time=extract_modified_time(soup),

        # Media
        video_url=extract_video_url(soup, url),
        audio_url=extract_audio_url(soup, url),
        duration=extract_duration(soup),

        # Social/Twitter
        twitter_handle=extract_twitter_handle(soup),
        twitter_card=extract_twitter_card(soup),

        # Technical
        canonical_url=extract_canonical_url(soup),
        favicon=extract_favicon(soup, url),
        theme_color=extract_theme_color(soup),
        keywords=extract_keywords(soup),
    )
```

### unfurl_url() - The Main Entry Point

```python
async def unfurl_url(url: str) -> UnfurlData:
    """Main entry point: Fetch URL and extract metadata."""
    html = await fetch_url(url)
    return parse_html(html, url)
```

Simple and clean - fetch then parse.

---

## 7. Error Handling Patterns

### The Importance of Good Error Handling

Network operations fail. A lot. Your code must handle:

- Timeouts (server too slow)
- Connection errors (network down)
- HTTP errors (404, 500, etc.)
- Invalid content (not HTML)
- Malformed HTML (parsing errors)

### Let Errors Propagate

In `unfurl.py`, we let errors propagate to the caller:

```python
async def unfurl_url(url: str) -> UnfurlData:
    html = await fetch_url(url)  # Might raise httpx.HTTPError
    return parse_html(html, url)
```

The API layer (`main.py`) will catch and handle these errors, returning appropriate responses.

### Why Not Catch Everything Here?

```python
# BAD - hides information
async def unfurl_url(url: str) -> UnfurlData:
    try:
        html = await fetch_url(url)
        return parse_html(html, url)
    except Exception:
        return None  # What went wrong? No way to know!
```

```python
# GOOD - let caller decide how to handle
async def unfurl_url(url: str) -> UnfurlData:
    html = await fetch_url(url)  # Raises on error
    return parse_html(html, url)

# In main.py:
try:
    data = await unfurl_url(url)
    return UnfurlResponse(success=True, data=data)
except httpx.TimeoutException:
    return UnfurlResponse(success=False, error="Request timed out")
except httpx.HTTPStatusError as e:
    return UnfurlResponse(success=False, error=f"HTTP {e.response.status_code}")
```

### Graceful Degradation

If some metadata is missing, we still return what we found:

```python
# Even if description and image are missing, we return the title
UnfurlData(
    url="https://example.com",
    title="Example Site",
    description=None,  # Not found, but that's OK
    image=None,        # Not found, but that's OK
    site_name=None,
)
```

This is "graceful degradation" - partial data is better than complete failure.

---

## 8. Security Considerations

### Content Length Limits

Malicious URLs could point to huge files:

```python
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

content_length = response.headers.get("content-length")
if content_length and int(content_length) > MAX_CONTENT_LENGTH:
    raise ValueError("Content too large")
```

Without this, someone could exhaust your server's memory.

### Content Type Validation

Only process HTML:

```python
content_type = response.headers.get("content-type", "")
if "text/html" not in content_type:
    raise ValueError(f"Not HTML: {content_type}")
```

This prevents processing PDFs, images, or other files.

### Timeout Protection

Always set timeouts:

```python
response = await client.get(url, timeout=10.0)
```

Without timeouts, a slow server could keep your connection open forever.

### User-Agent Identification

Every HTTP request includes a `User-Agent` header that tells the server what's making the request:

```
Browser:        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
Googlebot:      "Googlebot/2.1 (+http://www.google.com/bot.html)"
Our app:        "Mozilla/5.0 (compatible; LinkPreviewer/1.0)"
```

### Why Websites Care About User-Agent

Websites use User-Agent to decide:

| Decision | Example |
|----------|---------|
| **Content to serve** | Mobile vs desktop layout |
| **Caching behavior** | Bots get stale data, humans get fresh |
| **Rate limiting** | Bots get stricter request limits |
| **Access control** | Some sites block known scrapers |

### The Etiquette Question: Honest vs Sneaky

**Approach 1: Honest Bot Identification (Recommended)**

```python
USER_AGENT = "Mozilla/5.0 (compatible; LinkPreviewer/1.0; +https://yoursite.com)"
```

This honestly says: "I'm a bot called LinkPreviewer."

| Pros | Cons |
|------|------|
| Transparent and ethical | May get cached/stale data |
| Site admins can identify you | May get blocked by some sites |
| They can contact you if issues | Stricter rate limits |
| Respects their bot policies | |

**Approach 2: Pretend to be a Browser (Not Recommended)**

```python
# Mimics a real Chrome browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

| Pros | Cons |
|------|------|
| Gets fresh data | Deceptive |
| Rarely blocked | May violate Terms of Service |
| Same experience as users | Could get IP banned if detected |

### Real-World Example

When testing our Link Previewer against GitHub, you might notice:

```
Our app returns:     "az9713 has 81 repositories"
Browser shows:       "az9713 has 88 repositories"
```

GitHub serves cached metadata to bots but fresh data to browsers. This is intentional - it reduces server load from automated tools.

### What Major Services Do

| Service | Approach |
|---------|----------|
| Slack, Discord | Honest bot User-Agent |
| Googlebot, Bingbot | Honest bot User-Agent |
| Many web scrapers | Fake browser User-Agent |

### Our Choice

We use the honest approach:

```python
USER_AGENT = "Mozilla/5.0 (compatible; LinkPreviewer/1.0)"
```

Why? The slight data staleness is acceptable for link previews. If we needed 100% accurate data, we'd use official APIs (like GitHub's REST API) instead of scraping meta tags.

**Rule of thumb:** Be honest about what you are. If a site blocks bots, respect that decision rather than circumventing it.

---

## 9. Testing the Extraction

### Manual Testing

```python
import asyncio
from app.unfurl import unfurl_url

async def test():
    # Test various sites
    urls = [
        "https://github.com",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://twitter.com",
    ]

    for url in urls:
        try:
            result = await unfurl_url(url)
            print(f"\n{url}")
            print(f"  Title: {result.title}")
            print(f"  Description: {result.description[:50]}..." if result.description else "  Description: None")
            print(f"  Image: {result.image}")
        except Exception as e:
            print(f"\n{url}")
            print(f"  Error: {e}")

asyncio.run(test())
```

### Unit Testing (for later)

```python
from app.unfurl import parse_html, extract_title
from bs4 import BeautifulSoup

def test_extract_title_og():
    html = '<html><head><meta property="og:title" content="OG Title"></head></html>'
    soup = BeautifulSoup(html, "html.parser")
    assert extract_title(soup) == "OG Title"

def test_extract_title_fallback():
    html = '<html><head><title>HTML Title</title></head></html>'
    soup = BeautifulSoup(html, "html.parser")
    assert extract_title(soup) == "HTML Title"

def test_parse_html_complete():
    html = '''
    <html><head>
        <meta property="og:title" content="Test Title">
        <meta property="og:description" content="Test Description">
        <meta property="og:image" content="/image.png">
    </head></html>
    '''
    result = parse_html(html, "https://example.com")
    assert result.title == "Test Title"
    assert result.description == "Test Description"
    assert result.image == "https://example.com/image.png"
```

---

## 10. Commands Reference

### httpx Commands

```python
import httpx

# Async client
async with httpx.AsyncClient() as client:
    # GET request
    response = await client.get(url)

    # POST request
    response = await client.post(url, json={"key": "value"})

    # With headers
    response = await client.get(url, headers={"User-Agent": "Bot"})

    # With timeout
    response = await client.get(url, timeout=10.0)

    # Check status
    response.raise_for_status()  # Raises if 4xx/5xx

    # Get content
    text = response.text           # As string
    data = response.json()         # Parse JSON
    content = response.content     # Raw bytes
```

### BeautifulSoup Commands

```python
from bs4 import BeautifulSoup

# Parse HTML
soup = BeautifulSoup(html, "lxml")

# Find elements
soup.find("title")                        # First <title>
soup.find("meta", property="og:title")    # Meta with property
soup.find("meta", attrs={"name": "desc"}) # Meta with name
soup.find_all("meta")                     # All meta tags

# Access data
element.text                              # Inner text
element.string                            # Direct text child
element["attribute"]                      # Attribute value
element.get("attribute")                  # Attribute or None
element.name                              # Tag name
```

### URL Manipulation

```python
from urllib.parse import urljoin, urlparse

# Join URLs
urljoin("https://example.com/page", "/images/pic.png")
# → "https://example.com/images/pic.png"

# Parse URL
parsed = urlparse("https://example.com:8080/path?query=1")
parsed.scheme    # "https"
parsed.netloc    # "example.com:8080"
parsed.path      # "/path"
parsed.query     # "query=1"
```

---

## 11. Self-Check Questions

1. **Why do we use async/await for HTTP requests?**

   Answer: Async allows non-blocking I/O. While waiting for one URL to respond, the server can handle other requests. This dramatically improves throughput for I/O-bound operations.

2. **What is the extraction priority order, and why?**

   Answer: og:* → twitter:* → HTML. Open Graph is the most widely supported standard. Twitter cards are fallback for Twitter-specific sites. HTML tags are last resort for minimal pages.

3. **Why do we check content-type before parsing?**

   Answer: To avoid parsing non-HTML content. A URL might return PDF, JSON, or binary data. Trying to parse these as HTML wastes resources and could cause errors.

4. **What does urljoin() do and why is it needed?**

   Answer: It converts relative URLs to absolute. Images might be specified as "/images/pic.png" (relative) which needs to become "https://example.com/images/pic.png" (absolute) to be usable.

5. **Why do we set a User-Agent header?**

   Answer: To identify our bot. Some sites block requests without User-Agent. It's also good practice to let site owners know who's making requests.

6. **What is graceful degradation?**

   Answer: Returning partial results instead of failing completely. If a page has a title but no description, we return the title instead of throwing an error.

7. **Why do we let errors propagate instead of catching them in unfurl_url()?**

   Answer: To let the caller (main.py) decide how to handle them. Different errors might need different responses (timeout vs 404 vs parsing error).

8. **What could happen without the MAX_CONTENT_LENGTH check?**

   Answer: A malicious URL could point to a multi-gigabyte file, exhausting server memory and potentially crashing the application.

---

## Next Phase

Now that we can fetch and parse URLs, we will create the FastAPI application that exposes this functionality as an HTTP API in **Phase 5: FastAPI Application**.
