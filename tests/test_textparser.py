"""Test for textparser.py module."""
import pytest
from chuchu_scrapper.parsers.textparser import TextParser


@pytest.fixture
def text_parser():
    """Fixture to create a TextParser instance."""
    return TextParser()


def test_empty_html(text_parser):
    """Test parsing of empty HTML."""
    text_parser.feed("")
    assert text_parser.get_text() == ""


def test_simple_text(text_parser):
    """Test parsiing on plain text without HTML tags."""
    html = "Hello, World!"
    text_parser.feed(html)
    assert text_parser.get_text() == "Hello, World!"


def test_basic_html(text_parser):
    """Test parsing of basic HTML."""
    html = "<p>Hello, <b>World!</b></p>"
    text_parser.feed(html)
    assert text_parser.get_text() == "Hello, World!"


def test_nested_tags(text_parser):
    """Test parsing of nested HTML tags."""
    html = "<div><p>Hello, <b>World!</b></p></div>"
    text_parser.feed(html)
    assert text_parser.get_text() == "Hello, World!"


def test_ignore_script_style(text_parser):
    """Test ignoring script and style tags."""
    html = """
    <html>
        <head>
            <script>alert('test');</script>
        </head>
        <body>
                <p>Hello, World!</p>
            </body>
    </html>"""
    text_parser.feed(html)
    assert text_parser.get_text() == "Hello, World!"


def test_line_breaks(text_parser):
    """Test handling of line bbreaks with br, p, div tags."""
    html = "<div>Line 1<br>Line 2</div><p>Paragraph 1</p>"
    text_parser.feed(html)
    assert text_parser.get_text() == "Line 1\nLine 2\nParagraph 1"


def test_multiple_parses():
    """Test parser with multiple separate parses."""
    parser1 = TextParser()
    html1 = "<p>First parse</p>"
    parser1.feed(html1)
    result1 = parser1.get_text()

    parser2 = TextParser()
    html2 = "<div>Second parse</div>"
    parser2.feed(html2)
    result2 = parser2.get_text()

    assert result1 == "First parse"
    assert result2 == "Second parse"


def test_parametrized_input():
    """Test parser with various input types using parametrization."""
    test_cases = [
        ("<p>Simple paragraph</p>", "Simple paragraph"),
        ("<div>Text <b>with bold</b> formatting</div>", "Text with bold formatting"),
        ("<a href='#'>Link text</a>", "Link text"),
        ("<h1>Heading</h1><h2>Subheading</h2>", "Heading Subheading"),
    ]

    for html, expected in test_cases:
        parser = TextParser()
        parser.feed(html)
        assert parser.get_text() == expected


def test_html_entities():
    """Test handling of HTML entities."""
    parser = TextParser()
    html = "<p>Special chars: &lt; &gt; &amp; &quot; &apos;</p>"
    parser.feed(html)
    # HTMLParser automatically converts entities
    assert "Special chars: < > & \" '" in parser.get_text()
