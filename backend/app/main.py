"""
FastAPI Application for the Link Previewer API.

This module defines:
1. The FastAPI application instance
2. CORS middleware configuration
3. API endpoints (/unfurl, /health)
4. Error handling
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .models import UnfurlRequest, UnfurlResponse, UnfurlData
from .unfurl import unfurl_url


# Create the FastAPI application
app = FastAPI(
    title="Link Previewer API",
    description="Extract metadata (title, description, image) from URLs",
    version="1.0.0",
)


# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend (running on a different port/domain) to call our API
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Frontend URLs that can call this API
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    """
    Root endpoint - returns API info.
    Useful for checking if the API is running.
    """
    return {
        "name": "Link Previewer API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Used by deployment platforms (Railway, Kubernetes, etc.)
    to verify the service is running and healthy.
    """
    return {"status": "healthy"}


@app.post("/unfurl", response_model=UnfurlResponse)
async def unfurl(request: UnfurlRequest) -> UnfurlResponse:
    """
    Extract metadata from a URL.

    This is the main endpoint of the API. It:
    1. Receives a URL in the request body
    2. Fetches the HTML content from that URL
    3. Parses the HTML to extract metadata
    4. Returns the metadata in a structured format

    Args:
        request: UnfurlRequest containing the URL to process

    Returns:
        UnfurlResponse with success=True and data, or success=False and error
    """
    url_str = str(request.url)

    try:
        # Attempt to fetch and parse the URL
        data = await unfurl_url(url_str)
        return UnfurlResponse(success=True, data=data)

    except httpx.TimeoutException:
        # Request took too long
        return UnfurlResponse(
            success=False,
            error=f"Request timed out while fetching {url_str}"
        )

    except httpx.HTTPStatusError as e:
        # Server returned 4xx or 5xx error
        return UnfurlResponse(
            success=False,
            error=f"HTTP error {e.response.status_code} while fetching {url_str}"
        )

    except httpx.RequestError as e:
        # Network error (DNS failure, connection refused, etc.)
        return UnfurlResponse(
            success=False,
            error=f"Failed to connect to {url_str}: {type(e).__name__}"
        )

    except ValueError as e:
        # Our own validation errors (content too large, not HTML, etc.)
        return UnfurlResponse(
            success=False,
            error=str(e)
        )

    except Exception as e:
        # Unexpected error - log it and return generic message
        # In production, you would log this properly
        print(f"Unexpected error processing {url_str}: {e}")
        return UnfurlResponse(
            success=False,
            error="An unexpected error occurred while processing the URL"
        )


# This block runs when you execute: python -m app.main
# It starts the development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
    )
