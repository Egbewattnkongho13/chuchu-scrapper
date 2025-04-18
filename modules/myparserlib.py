"""HTML parsing utilities for text, image, and link extraction."""
from html.parser import HTMLParser
from typing import List, Dict
from urllib.parse import urljoin


class TextParser(HTMLParser):
    """Parser class to extract the clean text content."""

    def __init__(self):
        """Initialize the parser with an empty list for text content."""
        super().__init__()
        self.text_content = []
        self._ignore_tags = {'script', 'style', 'noscript', 'meta'}
        self._current_ignore = False

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Handle the start tag of the HTML element by ignoring specific tags."""
        if tag in self._ignore_tags:
            self._current_ignore = True

    def handle_endtag(self, tag: str):
        """Handle the end tag of the HTML element by resetting the ignore flag."""
        if tag in self._ignore_tags:
            self._current_ignore = False
        elif tag in ('br', 'p', 'div', 'section', 'article'):
            self.text_content.append('\n')

    def handle_data(self, data: str):
        """Handle the data within the HTML element by appending it."""
        if not self._current_ignore and data.strip():
            self.text_content.append(data.strip())

    def get_text(self):
        """Return the extracted text content as a single string."""
        text = ' '.join(self.text_content)
        lines = (line.strip() for line in text.splitlines())
        return '\n'.join(line for line in lines if line.strip())


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
        if tag == 'img':
            self._current_tag = tag
            self._current_attrs = dict(attrs)
            img_url = self._make_absolute(self._current_attrs.get('src'))

            if img_url:
                self.images.append({
                    'url': img_url,
                    'alt': self._current_attrs.get('alt', ''),
                    'attrs': self._current_attrs
                })

    def _make_absolute(self, url: str):
        """Convert a relative URL to an absolute URL using the base URL."""
        if not url or url.startswith(("javascript:", "mailto:", "tel:")):
            return None
        return urljoin(self.base_url, url)


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
        if tag == 'a':
            attrs_dict = dict(attrs)
            if href := attrs_dict.get('href'):
                if absolute_url := self._make_absolute(href):
                    self._current_url = absolute_url
                    self._current_title = attrs_dict.get('title', '')
                    self.links.append({
                        'url': absolute_url,
                        'title': self._current_title
                    })

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
        return [{
            'url': link['url'],
            'title': link['title']
        } for link in self.links if link['url']]
