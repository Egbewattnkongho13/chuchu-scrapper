"""Module for scraping website data."""

import argparse
import os
import time
from html.parser import HTMLParser
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests


def parse_args():
    """Parse command-line arguments for the chuchu-scrapper application."""
    parser = argparse.ArgumentParser(
        prog="chuchu-scrapper", description="A simple CLI scrapper application."
    )

    parser.add_argument("url", help="URL to scrape", type=str)
    parser.add_argument(
        "--type",
        help="Type of data to scrape",
        type=str,
        choices=["text", "image", "all"],
        required=True,
    )
    parser.add_argument(
        "--output",
        help="Directory to save files (default: ./output)",
        type=str,
        default="./output",
    )
    parser.add_argument(
        "--stdout", help="Print results to CLI instead of saving", action="store_true"
    )
    return parser.parse_args()


class ChuChuScrapper:
    """Web scraper that handles both text and image extraction."""

    def __init__(
        self,
        user_agent: str = "ChuChuScrapper/1.0",
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """Initialize the scraper with configuration options."""
        self.session = requests.Session()
        self.session.headers = {"User-Agent": user_agent}
        self.timeout = timeout
        self.max_retries = max_retries

    def scrape_text(self, url: str) -> Optional[str]:
        """Extract and return all text content from a webpage."""
        html = self._fetch_with_retry(url)
        if not html:
            return None

        parser = self._TextParser()
        parser.feed(html)
        return parser.get_text()

    def scrape_images(self, url: str) -> List[Dict]:
        """Extract all images from a webpage."""
        html = self._fetch_with_retry(url)
        if not html:
            return []

        parser = self._HTMLParser(url)
        parser.feed(html)
        return parser.images

    def download_images(self, images: List[Dict], output_dir: str) -> None:
        """Download images to specified directory."""
        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        for img in images:
            img_url = img["url"]
            if not img_url:
                continue

            try:
                response = self.session.get(img_url, stream=True, timeout=self.timeout)
                response.raise_for_status()

                filename = os.path.basename(urlparse(img_url).path)
                if not filename:
                    filename = f"image_{images.index(img)}.jpg"

                filepath = os.path.join(img_dir, filename)
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")

    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """Fetch HTML with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                if "text/html" in response.headers.get("Content-Type", ""):
                    return response.text
                return None
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"Failed after {self.max_retries} attempts: {e}")
                    return None
                time.sleep(2**attempt)
        return None

    class _TextParser(HTMLParser):
        """Parser for extracting clean text content."""

        def __init__(self):
            """Initialize the text parser."""
            super().__init__()
            self.text_parts = []
            self._ignore_tags = {"script", "style", "noscript", "meta"}
            self._current_ignore = False

        def handle_starttag(self, tag: str, attrs: List[tuple]):
            """Handle HTML start tags."""
            if tag in self._ignore_tags:
                self._current_ignore = True

        def handle_endtag(self, tag: str):
            """Handle HTML end tags."""
            if tag in self._ignore_tags:
                self._current_ignore = False
            elif tag in ("p", "br", "div", "section"):
                self.text_parts.append("\n")

        def handle_data(self, data: str):
            """Handle text data between tags."""
            if not self._current_ignore and data.strip():
                self.text_parts.append(data.strip())

        def get_text(self) -> str:
            """Return cleaned text content."""
            text = " ".join(self.text_parts)
            return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    class _HTMLParser(HTMLParser):
        """Parser for extracting structured HTML data."""

        def __init__(self, base_url: str):
            """Initialize the HTML parser with base URL."""
            super().__init__()
            self.base_url = base_url
            self.images = []
            self._current_tag = None
            self._current_attrs = {}

        def handle_starttag(self, tag: str, attrs: List[tuple]):
            """Handle HTML start tags and extract image data."""
            self._current_tag = tag
            self._current_attrs = dict(attrs)

            if tag == "img":
                img_url = self._make_absolute(self._current_attrs.get("src"))
                if img_url:
                    self.images.append(
                        {
                            "url": img_url,
                            "alt": self._current_attrs.get("alt", ""),
                            "attrs": self._current_attrs,
                        }
                    )

        def _make_absolute(self, url: str) -> Optional[str]:
            """Convert relative URLs to absolute."""
            if not url or url.startswith(("javascript:", "mailto:", "tel:")):
                return None
            return urljoin(self.base_url, url)


def save_text(content: str, output_dir: str) -> str:
    """Save text content to file and return path."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "scraped_text.txt")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
    except IOError as e:
        print(f"Error saving text: {e}")
        return ""


def main():
    """Execute the main scraping workflow."""
    args = parse_args()
    scraper = ChuChuScrapper()

    if not args.stdout:
        os.makedirs(args.output, exist_ok=True)

    if args.type in ["text", "all"]:
        text_content = scraper.scrape_text(args.url)
        if text_content:
            if args.stdout:
                print("\n=== SCRAPED TEXT ===\n")
                print(text_content)
            else:
                path = save_text(text_content, args.output)
                print(f"Text saved to: {path}")

    if args.type in ["image", "all"]:
        images = scraper.scrape_images(args.url)
        if images:
            if args.stdout:
                print("\n=== IMAGE URLs ===\n")
                for img in images:
                    print(img["url"])
            else:
                scraper.download_images(images, args.output)


if __name__ == "__main__":
    main()
