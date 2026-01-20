# Link Previewer

A microservice that extracts metadata from URLs, similar to how Slack, Discord, and Twitter generate link previews.

## Features

- Extracts Open Graph, Twitter Card, and standard HTML metadata
- Returns title, description, image, author, timestamps, and more
- Handles relative URLs, redirects, and error cases gracefully
- Fast async HTTP requests with configurable timeout
- React frontend with live preview

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, httpx, BeautifulSoup4
- **Frontend**: React, Vite
- **Deployment**: Render (backend), Vercel (frontend)

## API

### `POST /unfurl`

Extract metadata from a URL.

**Request:**
```json
{
  "url": "https://github.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://github.com",
    "title": "GitHub: Let's build from here",
    "description": "GitHub is where over 100 million developers shape the future of software...",
    "image": "https://github.githubassets.com/assets/github-logo-55c5b9a1fe52.png",
    "site_name": "GitHub",
    "type": "website",
    "favicon": "https://github.com/favicon.ico"
  }
}
```

### `GET /health`

Health check endpoint.

## Local Development

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Deployment

### Backend (Render.com)

1. Create a new Web Service on Render
2. Connect your GitHub repo
3. Set Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Import your GitHub repo on Vercel
2. Set Root Directory: `frontend`
3. Add environment variable: `VITE_API_URL` = your Render backend URL

## Extracted Metadata Fields

| Field | Source | Description |
|-------|--------|-------------|
| `title` | og:title, twitter:title, `<title>` | Page title |
| `description` | og:description, twitter:description, meta description | Page description |
| `image` | og:image, twitter:image | Preview image URL |
| `site_name` | og:site_name | Website name |
| `type` | og:type | Content type (website, article, video) |
| `locale` | og:locale | Language/region |
| `author` | article:author, author | Content author |
| `publisher` | article:publisher | Publisher name |
| `published_time` | article:published_time | Publication date |
| `modified_time` | article:modified_time | Last modified date |
| `video_url` | og:video | Video URL |
| `audio_url` | og:audio | Audio URL |
| `duration` | og:video:duration | Media duration |
| `twitter_handle` | twitter:creator, twitter:site | Twitter username |
| `twitter_card` | twitter:card | Twitter card type |
| `canonical_url` | link rel=canonical, og:url | Canonical URL |
| `favicon` | link rel=icon | Site icon |
| `theme_color` | theme-color | Brand color |
| `keywords` | keywords | Page keywords |

## License

MIT
