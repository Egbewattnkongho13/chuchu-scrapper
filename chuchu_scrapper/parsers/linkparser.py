"""HTML parsing utilities for link extraction."""

from html.parser import HTMLParser
from typing import Dict, List
from urllib.parse import urljoin


class LinkParser(HTMLParser):
    """Parser that returns links in the exact format needed for the report."""

    def __init__(self, base_url: str):
        """Initialize the link parser with base URL and empty links list."""
        super().__init__()
        self.links = []
        self.base_url = base_url
        self._current_url = None
        self._current_title = None

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Process anchor tags and extract href and title attributes."""
        if tag == "a":
            attrs_dict = dict(attrs)
            if href := attrs_dict.get("href"):
                if absolute_url := self._make_absolute(href):
                    self._current_url = absolute_url
                    self._current_title = attrs_dict.get("title", "")
                    self.links.append(
                        {"url": absolute_url, "title": self._current_title}
                    )

    def _make_absolute(self, url: str) -> str:
        """Convert relative URLs to absolute.

        Args:
            url: The URL to convert to absolute
        Returns:
            Absolute URL or None if invalid
        """
        if not url or url.startswith(("javascript:", "mailto:", "tel:", "#")):
            return None
        return urljoin(self.base_url, url)

    def get_links(self) -> List[Dict]:
        """Return all collected links with their titles.

        Returns:
            List of dictionaries containing 'url' and 'title' keys
        """
        return [
            {"url": link["url"], "title": link["title"]}
            for link in self.links
            if link["url"]
        ]
