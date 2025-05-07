"""Test for imaegparser.py module."""
# import pytest
from chuchu_scrapper.parsers.imageparser import ImageParser


def test_empty_html():
    """Test parser behaivior on empty HTML."""
    parser = ImageParser("https://example.com")
    parser.feed("")
    assert len(parser.images) == 0, "Parser should find no images in empty HTML."


def test_image_parser_extracts_images():
    """Test parser extracts image URLs from HTML."""
    base_url = "https://example.com"
    html_content = """
    <html>
        <body>
            <img src="/images/cat.jpg" alt="A cute cat">
            <img src="images/dog.jpg" alt="A loyal dog">
            <img src="https://othersite.com/bird.jpg" alt="A colourful bird">
            <img src="javascript:alert('Not an image')">
            <div>Not an image tag</div>
        </body>
    </html>
            """

    parser = ImageParser(base_url)
    parser.feed(html_content)

    assert len(parser.images) == 3, "Parser should find three images."

    assert parser.images[0]['url'] == "https://example.com/images/cat.jpg"
    assert parser.images[0]['alt'] == "A cute cat"

    assert parser.images[1]['url'] == "https://example.com/images/dog.jpg"
    assert parser.images[1]['alt'] == "A loyal dog"

    assert parser.images[2]['url'] == "https://othersite.com/bird.jpg"
    assert parser.images[2]['alt'] == "A colourful bird"


def test_make_absolute_url():
    """Test that relative URLs are properly converted to absolute URLs."""
    base_url = "https://example.com"
    parser = ImageParser(base_url)

    relative_url = "/images/cat.jpg"
    assert parser._make_absolute(relative_url) == "https://example.com/images/cat.jpg"

    relative_url = "images/dog.jpg"
    assert parser._make_absolute(relative_url) == "https://example.com/images/dog.jpg"

    relative_url = "https://other.com/image.jpg"
    assert parser._make_absolute(relative_url) == "https://other.com/image.jpg"

    assert parser._make_absolute("javascript:alert('Not an image')") is None
    assert parser._make_absolute("") is None
