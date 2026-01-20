"""
URL Extraction Logic for the Link Previewer API.

This module handles:
1. Fetching HTML content from URLs
2. Parsing HTML to extract metadata
3. Implementing fallback strategies for missing data

The extraction priority order is:
1. Open Graph meta tags (og:title, og:description, og:image)
2. Twitter Card meta tags (twitter:title, twitter:description, twitter:image)
3. Standard HTML elements (<title>, <meta name="description">)
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional
from .models import UnfurlData


# Configuration constants
REQUEST_TIMEOUT = 10.0  # seconds
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max to prevent memory issues
USER_AGENT = (
    "Mozilla/5.0 (compatible; LinkPreviewer/1.0; "
    "+https://github.com/your-username/link-previewer)"
)


async def fetch_url(url: str) -> str:
    """
    Fetch HTML content from a URL.

    Args:
        url: The URL to fetch

    Returns:
        The HTML content as a string

    Raises:
        httpx.HTTPError: If the request fails
        ValueError: If content is too large or not HTML
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

        # Raise exception for 4xx/5xx status codes
        response.raise_for_status()

        # Check content length to prevent memory issues
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content too large: {content_length} bytes")

        # Verify it's HTML content
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            raise ValueError(f"Not HTML content: {content_type}")

        return response.text


def extract_meta_tag(soup: BeautifulSoup, property_name: str) -> Optional[str]:
    """
    Extract content from a meta tag by property or name attribute.

    Tries both 'property' and 'name' attributes because:
    - Open Graph uses: <meta property="og:title" content="...">
    - Twitter uses: <meta name="twitter:title" content="...">
    - Standard uses: <meta name="description" content="...">

    Args:
        soup: BeautifulSoup parsed HTML
        property_name: The property/name to look for

    Returns:
        The content attribute value, or None if not found
    """
    # Try property attribute first (Open Graph style)
    tag = soup.find("meta", property=property_name)
    if tag and tag.get("content"):
        return tag["content"].strip()

    # Try name attribute (Twitter/standard style)
    tag = soup.find("meta", attrs={"name": property_name})
    if tag and tag.get("content"):
        return tag["content"].strip()

    return None


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract page title with fallback chain.

    Priority:
    1. og:title (Open Graph)
    2. twitter:title (Twitter Card)
    3. <title> tag (HTML standard)

    Args:
        soup: BeautifulSoup parsed HTML

    Returns:
        The title string, or None if not found
    """
    # Try Open Graph title
    title = extract_meta_tag(soup, "og:title")
    if title:
        return title

    # Try Twitter title
    title = extract_meta_tag(soup, "twitter:title")
    if title:
        return title

    # Fall back to <title> tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    return None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract page description with fallback chain.

    Priority:
    1. og:description (Open Graph)
    2. twitter:description (Twitter Card)
    3. <meta name="description"> (HTML standard)

    Args:
        soup: BeautifulSoup parsed HTML

    Returns:
        The description string, or None if not found
    """
    # Try Open Graph description
    description = extract_meta_tag(soup, "og:description")
    if description:
        return description

    # Try Twitter description
    description = extract_meta_tag(soup, "twitter:description")
    if description:
        return description

    # Fall back to standard meta description
    description = extract_meta_tag(soup, "description")
    if description:
        return description

    return None


def extract_image(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Extract preview image URL with fallback chain.

    Priority:
    1. og:image (Open Graph)
    2. twitter:image (Twitter Card)

    Handles relative URLs by converting them to absolute URLs.

    Args:
        soup: BeautifulSoup parsed HTML
        base_url: The original page URL for resolving relative paths

    Returns:
        The absolute image URL, or None if not found
    """
    from urllib.parse import urljoin

    # Try Open Graph image
    image = extract_meta_tag(soup, "og:image")
    if image:
        # Convert relative URL to absolute
        return urljoin(base_url, image)

    # Try Twitter image
    image = extract_meta_tag(soup, "twitter:image")
    if image:
        return urljoin(base_url, image)

    return None


def extract_site_name(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract site name from Open Graph tags.

    Args:
        soup: BeautifulSoup parsed HTML

    Returns:
        The site name, or None if not found
    """
    return extract_meta_tag(soup, "og:site_name")


def parse_html(html: str, url: str) -> UnfurlData:
    """
    Parse HTML content and extract all metadata.

    This is the main parsing function that orchestrates
    extraction of all metadata fields.

    Args:
        html: The HTML content to parse
        url: The original URL (for resolving relative paths)

    Returns:
        UnfurlData with all extracted metadata
    """
    # Parse HTML with lxml for speed (falls back to html.parser if unavailable)
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    return UnfurlData(
        url=url,
        title=extract_title(soup),
        description=extract_description(soup),
        image=extract_image(soup, url),
        site_name=extract_site_name(soup),
    )


async def unfurl_url(url: str) -> UnfurlData:
    """
    Main entry point: Fetch a URL and extract its metadata.

    This function combines fetching and parsing into a single
    async operation. It's the function that main.py will call.

    Args:
        url: The URL to unfurl

    Returns:
        UnfurlData with extracted metadata

    Raises:
        httpx.HTTPError: If fetching fails
        ValueError: If content is invalid
    """
    html = await fetch_url(url)
    return parse_html(html, url)
