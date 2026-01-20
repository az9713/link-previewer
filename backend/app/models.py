"""
Data models for the Link Previewer API.

These Pydantic models define:
- What the API accepts (UnfurlRequest)
- What the API returns (UnfurlData, UnfurlResponse)
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class UnfurlRequest(BaseModel):
    """
    Input model: The URL to extract metadata from.

    HttpUrl validates that the string is a valid HTTP/HTTPS URL.
    Invalid URLs will automatically return a 422 error.
    """
    url: HttpUrl


class UnfurlData(BaseModel):
    """
    The extracted metadata from a URL.

    All fields are Optional because a webpage might not have any
    particular piece of metadata available.

    Fields are organized by category:
    - Basic: url, title, description, image, site_name
    - Content type: type, locale
    - Authorship: author, publisher
    - Timestamps: published_time, modified_time
    - Media: video_url, audio_url, duration
    - Social: twitter_handle, twitter_card
    - Technical: canonical_url, favicon, theme_color, keywords
    """
    # Basic metadata (most commonly used)
    url: str                              # The original URL (echoed back)
    title: Optional[str] = None           # Page title
    description: Optional[str] = None     # Page description
    image: Optional[str] = None           # Preview image URL
    site_name: Optional[str] = None       # Website name

    # Content type information
    type: Optional[str] = None            # og:type (website, article, video, etc.)
    locale: Optional[str] = None          # og:locale (en_US, etc.)

    # Authorship
    author: Optional[str] = None          # Content author
    publisher: Optional[str] = None       # Publisher name

    # Timestamps
    published_time: Optional[str] = None  # When content was published
    modified_time: Optional[str] = None   # When content was last modified

    # Media (for video/audio content)
    video_url: Optional[str] = None       # Direct video URL
    audio_url: Optional[str] = None       # Direct audio URL
    duration: Optional[str] = None        # Media duration in seconds

    # Social/Twitter specific
    twitter_handle: Optional[str] = None  # @username of content creator
    twitter_card: Optional[str] = None    # Twitter card type

    # Technical metadata
    canonical_url: Optional[str] = None   # Canonical URL
    favicon: Optional[str] = None         # Site icon URL
    theme_color: Optional[str] = None     # Brand/theme color
    keywords: Optional[List[str]] = None  # Page keywords as list


class UnfurlResponse(BaseModel):
    """
    API response wrapper.

    success: Whether extraction worked
    data: The extracted metadata (if successful)
    error: Error message (if failed)
    """
    success: bool
    data: Optional[UnfurlData] = None
    error: Optional[str] = None
