"""Tests for the ChuChuScrapper class."""
# import os
import pytest
# from unittest.mock import patch, MagicMock
import requests_mock
from pathlib import Path

# Import and test the ChuChuScrapper class and its methods.
from chuchu_scrapper.scrapper import ChuChuScrapper

FIXTURES_PATH = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_html():
    """Load sample HTML fixture for testing."""
    with open(FIXTURES_PATH / "sample_html.html", "r", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def scrapper():
    """Create a ChuChuScrapper instance for testing."""
    return ChuChuScrapper(timeout=1, max_retries=1)


class TestChuChuScrapper:
    """Test for the ChuChuScrapper class."""

    def __init__(self):
        """Test that scrapper initializes with correct parameters."""
        scrapper = ChuChuScrapper(user_agent="TestAgent", timeout=5, max_retries=3)

        assert scrapper.timeout == 5
        assert scrapper.max_retries == 3
        assert scrapper.session.headers["User-Agent"] == "TestAgent"

    def test_fetch_with_retry_success(self, scrapper, sample_html):
        """Test successful fetch with retry logic."""
        test_url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(
                test_url, text=sample_html,
                headers={"Content-Type": "text/html; charset=utf-8"})

            result = scrapper._fetch_with_retry(test_url)

            assert result == sample_html
            assert m.call_count == 1
