"""
Data models for the Link Previewer API.

These Pydantic models define:
- What the API accepts (UnfurlRequest)
- What the API returns (UnfurlData, UnfurlResponse)
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional


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
    
    All fields are Optional because a webpage might not have:
    - A title (rare but possible)
    - A description (common on minimal pages)
    - An image (many pages lack og:image)
    """
    url: str              # The original URL (echoed back)
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site_name: Optional[str] = None


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
