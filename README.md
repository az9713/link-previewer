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

### Prerequisites: Push to GitHub

Before deploying, your code must be on GitHub:

**Option 1: Create repo manually**
1. Go to https://github.com/new
2. Name: `link-previewer`, Public, don't initialize with README
3. Run:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/link-previewer.git
   git push -u origin main
   ```

**Option 2: Use GitHub CLI (if installed)**
```bash
gh repo create link-previewer --public --source=. --remote=origin --push
```

### Backend (Render.com)

1. Create account at https://render.com (use GitHub sign-in)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   | Setting | Value |
   |---------|-------|
   | Root Directory | `backend` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free |
5. Click **"Create Web Service"**
6. Wait for deployment (2-5 minutes)
7. Note your URL: `https://your-service.onrender.com`

### Frontend (Vercel)

1. Create account at https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repo
4. Configure:
   | Setting | Value |
   |---------|-------|
   | Root Directory | `frontend` |
   | Environment Variable | `VITE_API_URL` = your Render URL |
5. Click **"Deploy"**
6. Note your URL: `https://your-app.vercel.app`

### Post-Deployment: Configure CORS

**Critical step!** After frontend deployment:
1. Go to Render dashboard → your service → **Environment**
2. Add environment variable:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** `https://your-app.vercel.app,http://localhost:5173,http://localhost:3000`
3. Render will auto-redeploy

### Free Tier Notes

**Important: Don't mistake a sleeping service for a broken site!**

- **Render free tier:** Services automatically "sleep" after 15 minutes of no requests
- **First request after sleep:** Takes **~50 seconds** while the service wakes up (cold start)
- **Subsequent requests:** Fast (~200ms) until the next idle period
- **Vercel:** No sleep issues - frontend loads instantly from global CDN

**What you'll see:**
1. Visit your app after it's been idle for 15+ minutes
2. Enter a URL and click "Preview"
3. The spinner appears and seems stuck for ~50 seconds
4. **This is normal!** The backend is waking up
5. Once loaded, everything works fast until the next idle period

**Tip:** To keep the service awake, use a free monitoring service like [UptimeRobot](https://uptimerobot.com) to ping your `/health` endpoint every 14 minutes.

For detailed deployment guides, see:
- [`docs/tutorials/phase-10-deploy-render.md`](docs/tutorials/phase-10-deploy-render.md)
- [`docs/tutorials/phase-11-deploy-vercel.md`](docs/tutorials/phase-11-deploy-vercel.md)
- [`docs/deployment-troubleshooting.md`](docs/deployment-troubleshooting.md)

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

## Acknowledgements

This project was built with AI assistance:

- **Code & Documentation:** All source code and documentation were generated by [Claude Code](https://claude.ai/claude-code) powered by Claude Opus 4.5
- **Deployment:** Deployment to Vercel and Render was accomplished in large part by [Claude in Chrome](https://chromewebstore.google.com/detail/claude-in-chrome/), with the human providing only minimal authorization clicks

This demonstrates the capability of AI-assisted software development, from initial code generation through production deployment.

## License

MIT
