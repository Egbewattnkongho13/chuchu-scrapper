"""HTML Parser to extract image URLs from a website."""

from html.parser import HTMLParser
from typing import List
from urllib.parse import urljoin


class ImageParser(HTMLParser):
    """Parser class to extract image URLs from the HTML website."""

    def __init__(self, base_url: str):
        """Initialize the parser with base URL and empty image list."""
        super().__init__()
        self.images = []
        self.base_url = base_url
        self._current_tag = None
        self._current_attrs = {}

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Handle the start tag of the HTML element checking for images."""
        if tag == "img":
            self._current_tag = tag
            self._current_attrs = dict(attrs)
            img_url = self._make_absolute(self._current_attrs.get("src"))

            if img_url:
                self.images.append(
                    {
                        "url": img_url,
                        "alt": self._current_attrs.get("alt", ""),
                        "attrs": self._current_attrs,
                    }
                )

    def _make_absolute(self, url: str):
        """Convert a relative URL to an absolute URL using the base URL."""
        if not url or url.startswith(("javascript:", "mailto:", "tel:")):
            return None
        return urljoin(self.base_url, url)
