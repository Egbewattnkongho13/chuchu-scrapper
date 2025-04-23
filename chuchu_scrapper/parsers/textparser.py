"""HTML parsing utilities for text extraction."""

from html.parser import HTMLParser
from typing import List


class TextParser(HTMLParser):
    """Parser class to extract the clean text content."""

    def __init__(self):
        """Initialize the parser with an empty list for text content."""
        super().__init__()
        self.text_content = []
        self._ignore_tags = {"script", "style", "noscript", "meta"}
        self._current_ignore = False

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Handle the start tag of the HTML element by ignoring specific tags."""
        if tag in self._ignore_tags:
            self._current_ignore = True

    def handle_endtag(self, tag: str):
        """Handle the end tag of the HTML element by resetting the ignore flag."""
        if tag in self._ignore_tags:
            self._current_ignore = False
        elif tag in ("br", "p", "div", "section", "article"):
            self.text_content.append("\n")

    def handle_data(self, data: str):
        """Handle the data within the HTML element by appending it."""
        if not self._current_ignore and data.strip():
            self.text_content.append(data.strip())

    def get_text(self):
        """Return the extracted text content as a single string."""
        text = " ".join(self.text_content)
        lines = (line.strip() for line in text.splitlines())
        return "\n".join(line for line in lines if line.strip())
