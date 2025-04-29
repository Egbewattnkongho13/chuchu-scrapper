"""Tests for the ChuChuScrapper class."""
import os
import pytest
from unittest.mock import patch, MagicMock
import requests_mock
from pathlib import Path

# Import and test the ChuChuScrapper class and its methods.
from chuchu_scrapper.scrapper import ChuChuScrapper

FIXTURES_PATH = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample():
    """Load sample HTML fixture for testing."""
    with open(FIXTURES_PATH / "sample.html", "r", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def scrapper():
    """Create a ChuChuScrapper instance for testing."""
    return ChuChuScrapper(timeout=1, max_retries=1)


class TestChuChuScrapper:
    """Test for the ChuChuScrapper class."""

    def test_initialization(self):
        """Test that scrapper initializes with correct parameters."""
        scrapper = ChuChuScrapper(user_agent="TestAgent", timeout=5, max_retries=3)

        assert scrapper.timeout == 5
        assert scrapper.max_retries == 3
        assert scrapper.session.headers["User-Agent"] == "TestAgent"

    def test_fetch_with_retry_success(self, scrapper, sample):
        """Test successful fetch with retry logic."""
        test_url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(
                test_url, text=sample,
                headers={"Content-Type": "text/html; charset=utf-8"})

            result = scrapper._fetch_with_retry(test_url)

            assert result == sample
            assert m.call_count == 1

    def test_fetch_with_retry_failure(self, scrapper):
        """Test fetch with  all retries failing."""
        test_url = "https://nonexistent.example.com"

        with requests_mock.Mocker() as m:
            m.get(test_url, status_code=404)

            result = scrapper._fetch_with_retry(test_url)

            assert result is None
            assert m.call_count == 1

    def test_fetch_non_html_content(self, scrapper):
        """Test fetch when content is not HTML."""
        test_url = "https://example.comm/image.jpg"

        with requests_mock.Mocker() as m:
            m.get(
                test_url,
                content=b"Not HTML content",
                headers={"Content-Type": "image/jpeg"})

            result = scrapper._fetch_with_retry(test_url)

            assert result is None

    @patch("chuchu_scrapper.scrapper.TextParser")
    def test_scrape_text(self, mock_text_parser, scrapper, sample):
        """Test text scrapping method."""
        test_url = "https://example.com"
        expected_text = "Sample extracted text"

        parser_instance = MagicMock()
        parser_instance.get_text.return_value = expected_text
        mock_text_parser.return_value = parser_instance

        with requests_mock.Mocker() as m:
            m.get(
                test_url,
                text=sample,
                headers={"Content-Type": "text/html; charset=utf-8"})

            result = scrapper.scrape_text(test_url)

            assert result == expected_text
            parser_instance.feed.assert_called_once_with(sample)
            parser_instance.get_text.assert_called_once()

    @patch("chuchu_scrapper.scrapper.ImageParser")
    def test_scrape_images(self, mock_image_parser, scrapper, sample):
        """Test image scrapping method."""
        test_url = "https://example.com"
        expected_images = [
            {"url": "https://example.com/image1.jpg", "alt": "Image 1"},
            {"url": "https://example.com/image2.png", "alt": "Image 2"}
        ]

        parser_instance = MagicMock()
        parser_instance.images = expected_images
        mock_image_parser.return_value = parser_instance

        with requests_mock.Mocker() as m:
            m.get(
                test_url,
                text=sample,
                headers={"Content-Type": "text/html; charset=utf-8"})

            result = scrapper.scrape_images(test_url)

            assert result == expected_images
            parser_instance.feed.assert_called_once_with(sample)
            mock_image_parser.assert_called_once_with(test_url)

    @patch("chuchu_scrapper.scrapper.LinkParser")
    def test_scrape_links(self, mock_link_parser, scrapper, sample):
        """Test link scrapping method."""
        test_url = "https://example.com"
        expected_links = [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": "Page 2"}
        ]

        parser_instance = MagicMock()
        parser_instance.get_links.return_value = expected_links
        mock_link_parser.return_value = parser_instance

        with requests_mock.Mocker() as m:
            m.get(
                test_url,
                text=sample,
                headers={"Content-Type": "text/html; charset=utf-8"})

            result = scrapper.scrape_links(test_url)

            assert result == expected_links
            parser_instance.feed.assert_called_once_with(sample)
            mock_link_parser.assert_called_once_with(test_url)

    def test_format_links_report(self, scrapper):
        """Test formatting of links report."""
        links = [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": ""}
        ]

        result = scrapper.format_links_report(links)

        assert "LINK 1" in result
        assert "URL: https://example.com/page1" in result
        assert "Anchor: Page 1" in result
        assert "LINK 2" in result
        assert "URL: https://example.com/page2" in result
        assert "Anchor: " in result

    def test_save_text(self, scrapper, tmp_path):
        """Test saving text content to file."""
        content = "sample text content"
        output_path = tmp_path / "output"

        filepath = scrapper.save_text(content, str(output_path))

        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as file:
            saved_content = file.read()
            assert saved_content == content

    def test_save_links(self, scrapper, tmp_path):
        """Test saving links to file."""
        links = [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": ""}
        ]
        output_path = tmp_path / "output"

        scrapper.save_links(links, str(output_path))

        filepath = output_path/"links_report.txt"
        assert os.path.exists(filepath)
