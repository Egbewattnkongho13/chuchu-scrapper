"""
Module for collecting or 'scraping' information from websites.

This module provides functionality for command-line interface
application to extract text, images,
and links from web pages using HTTP request and HTML parsing.
"""

import os
import time
from typing import Dict, List
from urllib.parse import urlparse

import requests

from chuchu_scrapper.parsers.imageparser import ImageParser
from chuchu_scrapper.parsers.linkparser import LinkParser
from chuchu_scrapper.parsers.textparser import TextParser


class ChuChuScrapper:
    """
    Main worker class for the web scraper.

    This class handles the fetching of web content and extraction of different
    types of data (text, images, links) from web pages.
    """

    def __init__(self, user_agent="ChuChuScrapper/1.0", timeout=10, max_retries=4):
        """
        Initialize the scraper with configurable parameters.

        Parameters:
            user_agent (str): User agent string to use in HTTP requests.
            timeout (int): Timeout in seconds for HTTP requests.
            max_retries (int): Maximum number of retry attempts for failed requests.
        """
        self.session = requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.session.headers.update({"User-Agent": user_agent})

    def scrape_text(self, url):
        """
        Scrape text data from the given URL.

        Parameters:
            url (str): The URL of the webpage to scrape.

        Returns:
            str or None: Extracted text content from the webpage.
        """
        webpage_content = self._fetch_with_retry(url)
        if not webpage_content:
            return None

        textparser = TextParser()
        textparser.feed(webpage_content)
        return textparser.get_text()

    def scrape_images(self, url: str) -> List[Dict]:
        """
        Scrape image data from the given URL.

        Parameters:
            url (str): The URL of the webpage to scrape.

        Returns:
            List[Dict] or None: A list of dictionaries containing image information
                              (url, alt text, etc.).
        """
        webpage_content = self._fetch_with_retry(url)
        if not webpage_content:
            return None

        imageparser = ImageParser(url)
        imageparser.feed(webpage_content)
        return imageparser.images

    def scrape_links(self, url) -> List[Dict]:
        """
        Scrape links from the given URL.

        Parameters:
            url (str): The URL of the webpage to scrape.

        Returns:
            List[Dict] or None: A list of dictionaries containing link information
                              (url and title).
        """
        webpage_content = self._fetch_with_retry(url)
        if not webpage_content:
            return None

        parsed = urlparse(url)
        base_url = {parsed.scheme} + "://" + {parsed.netloc}

        linkparser = LinkParser(base_url)
        linkparser.feed(webpage_content)
        return linkparser.get_links()

    def format_links_report(self, links: list) -> str:
        """
        Format links into a numbered report style.

        Parameters:
            links (List[Dict]): A list of link dictionaries to format.

        Returns:
            str: A formatted string containing the links report.
        """
        report = []
        for i, link in enumerate(links, 1):
            report.append(
                f"LINK {i}\n"
                f"URL: {link['url']}\n"
                f"Anchor: {link.get('title', '')}\n"
                f"{'-'*40}"
            )
        return "\n".join(report)

    def _fetch_with_retry(self, url):
        """
        Fetch the webpage content with retry logic.

        Parameters:
            url (str): The URL to fetch content from.

        Returns:
            str or None: The HTML content of the webpage as text, or None if all
                        retry attempts failed or if the response is not HTML.

        This method implements exponential backoff for retries.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                if "text/html" not in response.headers.get("Content-Type", ""):
                    print(f"URL {url} does not contain HTML content.")
                    return None
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2**attempt)
                else:
                    print(
                        f"""Failed to fetch {url} after {self.max_retries}
                    attempts: {e}"""
                    )
                    return None

    def save_text(self, content: str, output_dir: str):
        """
        Save the scraped text content to a file.

        Parameters:
            content (str): Text content to save.
            output_dir (str): Directory to save the file.

        Returns:
            str: Path to the saved file.

        This method creates the output directory if it doesn't exist.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "scraped_text.txt")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Text saved to {filepath}")

    def download_images(self, parser_images: list, output_dir: str):
        """
        Download images from parser results to the specified directory.

        Parameters:
            parser_images (List[Dict]): List of image dictionaries
                                         from HTMLParser.images
                              (format: [{"url": str, "alt": str, ...}])
            output_dir (str): Target directory path.

        This method creates the output directory and an "images"
        subdirectory if they don't exist.
        Each image is downloaded and saved with its original filename
        or a generated name.

        Exceptions:
            Catches and logs RequestException if image download fails.
        """
        os.makedirs(output_dir, exist_ok=True)

        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        for img in parser_images:
            img_url = img["url"]
            if not img_url:
                continue

            try:
                response = self.session.get(img_url, stream=True, timeout=self.timeout)
                response.raise_for_status()

                filename = os.path.basename(urlparse(img_url).path)
                if not filename:
                    filename = f"image_{parser_images.index(img)}.jpg"

                filepath = os.path.join(img_dir, filename)

                with open(filepath, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                print(f"Downloaded: {filename}")

            except requests.exceptions.RequestException as e:
                print(f"Failed to download {img_url}: {e}")

    def save_links(self, links: list, output_dir: str):
        """
        Save formatted link report to a file.

        Parameters:
            links (List[Dict]): List of link dictionaries to save.
            output_dir (str): Directory to save the file.

        This method creates the output directory if it doesn't exist and
        saves the links report to 'scraped_links.txt'.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "scraped_links.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.format_links_report(links))
        print(f"Links saved to {filepath}")
