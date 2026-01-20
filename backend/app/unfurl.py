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
from typing import Optional, List
from urllib.parse import urljoin
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
    """
    # Try Open Graph image
    image = extract_meta_tag(soup, "og:image")
    if image:
        return urljoin(base_url, image)

    # Try Twitter image
    image = extract_meta_tag(soup, "twitter:image")
    if image:
        return urljoin(base_url, image)

    return None


def extract_site_name(soup: BeautifulSoup) -> Optional[str]:
    """Extract site name from Open Graph tags."""
    return extract_meta_tag(soup, "og:site_name")


def extract_type(soup: BeautifulSoup) -> Optional[str]:
    """Extract content type (website, article, video, etc.)."""
    return extract_meta_tag(soup, "og:type")


def extract_locale(soup: BeautifulSoup) -> Optional[str]:
    """Extract locale/language setting."""
    return extract_meta_tag(soup, "og:locale")


def extract_author(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract author with fallback chain.

    Priority:
    1. article:author (Open Graph)
    2. author meta tag
    3. twitter:creator (without @)
    """
    author = extract_meta_tag(soup, "article:author")
    if author:
        return author

    author = extract_meta_tag(soup, "author")
    if author:
        return author

    return None


def extract_publisher(soup: BeautifulSoup) -> Optional[str]:
    """Extract publisher name."""
    publisher = extract_meta_tag(soup, "article:publisher")
    if publisher:
        return publisher

    publisher = extract_meta_tag(soup, "publisher")
    if publisher:
        return publisher

    return None


def extract_published_time(soup: BeautifulSoup) -> Optional[str]:
    """Extract publication timestamp."""
    time = extract_meta_tag(soup, "article:published_time")
    if time:
        return time

    time = extract_meta_tag(soup, "og:published_time")
    if time:
        return time

    time = extract_meta_tag(soup, "date")
    if time:
        return time

    return None


def extract_modified_time(soup: BeautifulSoup) -> Optional[str]:
    """Extract last modified timestamp."""
    time = extract_meta_tag(soup, "article:modified_time")
    if time:
        return time

    time = extract_meta_tag(soup, "og:updated_time")
    if time:
        return time

    return None


def extract_video_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract video URL for video content."""
    video = extract_meta_tag(soup, "og:video:url")
    if video:
        return urljoin(base_url, video)

    video = extract_meta_tag(soup, "og:video")
    if video:
        return urljoin(base_url, video)

    video = extract_meta_tag(soup, "og:video:secure_url")
    if video:
        return urljoin(base_url, video)

    return None


def extract_audio_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract audio URL for audio content."""
    audio = extract_meta_tag(soup, "og:audio:url")
    if audio:
        return urljoin(base_url, audio)

    audio = extract_meta_tag(soup, "og:audio")
    if audio:
        return urljoin(base_url, audio)

    return None


def extract_duration(soup: BeautifulSoup) -> Optional[str]:
    """Extract media duration in seconds."""
    duration = extract_meta_tag(soup, "og:video:duration")
    if duration:
        return duration

    duration = extract_meta_tag(soup, "video:duration")
    if duration:
        return duration

    return None


def extract_twitter_handle(soup: BeautifulSoup) -> Optional[str]:
    """Extract Twitter handle of content creator."""
    handle = extract_meta_tag(soup, "twitter:creator")
    if handle:
        return handle

    handle = extract_meta_tag(soup, "twitter:site")
    if handle:
        return handle

    return None


def extract_twitter_card(soup: BeautifulSoup) -> Optional[str]:
    """Extract Twitter card type."""
    return extract_meta_tag(soup, "twitter:card")


def extract_canonical_url(soup: BeautifulSoup) -> Optional[str]:
    """Extract canonical URL from link tag."""
    link = soup.find("link", rel="canonical")
    if link and link.get("href"):
        return link["href"]

    canonical = extract_meta_tag(soup, "og:url")
    if canonical:
        return canonical

    return None


def extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Extract favicon URL.

    Tries multiple common favicon link relations.
    """
    # Try various rel values for favicons
    for rel in ["icon", "shortcut icon", "apple-touch-icon"]:
        link = soup.find("link", rel=rel)
        if link and link.get("href"):
            return urljoin(base_url, link["href"])

    # Try array-style rel attribute
    link = soup.find("link", rel=lambda x: x and "icon" in x if isinstance(x, list) else x == "icon")
    if link and link.get("href"):
        return urljoin(base_url, link["href"])

    return None


def extract_theme_color(soup: BeautifulSoup) -> Optional[str]:
    """Extract theme/brand color."""
    return extract_meta_tag(soup, "theme-color")


def extract_keywords(soup: BeautifulSoup) -> Optional[List[str]]:
    """
    Extract keywords as a list.

    Keywords are typically comma-separated in the meta tag.
    """
    keywords_str = extract_meta_tag(soup, "keywords")
    if keywords_str:
        # Split by comma and clean up whitespace
        keywords = [k.strip() for k in keywords_str.split(",")]
        # Filter out empty strings
        keywords = [k for k in keywords if k]
        return keywords if keywords else None

    return None


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
