"""Test for linkparser.py module."""
# import pytest
from chuchu_scrapper.parsers.linkparser import LinkParser


class TestLinkParser:
    """Test suite for LinkParser class."""

    def test_empty_html(self):
        """Test that parser returns empty list for empty HTML."""
        parser = LinkParser("https://example.com")
        parser.feed("")
        assert parser.get_links() == []

    def test_no_links(self):
        """Test HTML with no links."""
        parser = LinkParser("https://example.com")
        html = """
        <html>
        <body>
            <h1>No links here</h1>
            <p>This is just text</p>
        </body>
        </html>
        """
        parser.feed(html)
        assert parser.get_links() == []

    def test_basic_links(self):
        """Test basic link extraction."""
        parser = LinkParser("https://example.com")
        html = """
        <html>
        <body>
            <a href="/page1.html">Page 1</a>
            <a href="page2.html" title="Second Page">Page 2</a>
            <a href="https://othersite.com/page3" title="External">External Link</a>
        </body>
        </html>
        """
        parser.feed(html)
        links = parser.get_links()

        assert len(links) == 3
        assert links[0] == {"url": "https://example.com/page1.html", "title": ""}
        assert links[1] == {
            "url": "https://example.com/page2.html", "title": "Second Page"
            }
        assert links[2] == {
            "url": "https://othersite.com/page3", "title": "External"
            }

    def test_invalid_links(self):
        """Test that parser correctly filters invalid links."""
        parser = LinkParser("https://example.com")
        html = """
        <html>
        <body>
            <a href="javascript:void(0)">JavaScript</a>
            <a href="mailto:user@example.com">Email</a>
            <a href="tel:+1234567890">Phone</a>
            <a href="#">Anchor</a>
            <a href="">Empty</a>
            <a>No href</a>
            <a href="https://valid.com">Valid link</a>
        </body>
        </html>
        """
        parser.feed(html)
        links = parser.get_links()

        assert len(links) == 1
        assert links[0]["url"] == "https://valid.com"

    def test_nested_links(self):
        """Test links with nested HTML elements."""
        parser = LinkParser("https://example.com")
        html = """
        <html>
        <body>
            <a href="/nested.html"
            title="Nested Link"><span>Nested <strong>Content</strong></span></a>
        </body>
        </html>
        """
        parser.feed(html)
        links = parser.get_links()

        assert len(links) == 1
        assert links[0] == {
            "url": "https://example.com/nested.html", "title": "Nested Link"
            }

    def test_duplicate_links(self):
        """Test that duplicate links are preserved."""
        parser = LinkParser("https://example.com")
        html = """
        <html>
        <body>
            <a href="/page.html">First</a>
            <a href="/page.html">Second</a>
            <a href="/page.html">Third</a>
        </body>
        </html>
        """
        parser.feed(html)
        links = parser.get_links()

        assert len(links) == 3
        assert all(link["url"] == "https://example.com/page.html" for link in links)

    def test_make_absolute_url(self):
        """Test URL conversion functionality."""
        parser = LinkParser("https://example.com/base/")

        assert parser._make_absolute("https://other.com/page") == "https://other.com/page"
        assert parser._make_absolute("http://other.net/page") == "http://other.net/page"

        assert parser._make_absolute("/page.html") == "https://example.com/page.html"
        assert parser._make_absolute("page.html") == "https://example.com/base/page.html"
        assert parser._make_absolute("../up.html") == "https://example.com/up.html"

        assert parser._make_absolute("javascript:alert()") is None
        assert parser._make_absolute("mailto:user@example.com") is None
        assert parser._make_absolute("tel:+1234567890") is None
        assert parser._make_absolute("#anchor") is None
        assert parser._make_absolute("") is None

    def test_get_links_method(self):
        """Test that get_links returns properly formatted data."""
        parser = LinkParser("https://example.com")

        parser.links = [
            {"url": "https://example.com/valid", "title": "Valid"},
            {"url": None, "title": "Invalid"},
            {"url": "https://example.com/another", "title": ""}
        ]

        links = parser.get_links()
        assert len(links) == 2
        assert links[0]["url"] == "https://example.com/valid"
        assert links[0]["title"] == "Valid"
        assert links[1]["url"] == "https://example.com/another"
        assert links[1]["title"] == ""

    def test_complex_html(self):
        """Test parser with complex HTML containing various elements."""
        parser = LinkParser("https://example.com")
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <header>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about" title="About Us">About</a>
                </nav>
            </header>
            <main>
                <article>
                    <p>Check out our <a href="/products">products</a> page!</p>
                    <div>
                        <a href="javascript:void(0)">Invalid</a>
                        <a href="https://external.org" title="External Site">External</a>
                    </div>
                </article>
            </main>
            <footer>
                <a href="#top">Back to top</a>
                <a href="/contact">Contact</a>
            </footer>
        </body>
        </html>
        """
        parser.feed(html)
        links = parser.get_links()

        assert len(links) == 5
        urls = [link["url"] for link in links]
        assert "https://example.com/" in urls
        assert "https://example.com/about" in urls
        assert "https://example.com/products" in urls
        assert "https://example.com/contact" in urls
        assert "https://external.org" in urls

    def test_reset_functionality(self):
        """Test that parser can be reset and reused."""
        parser = LinkParser("https://example.com")

        parser.feed('<a href="/first">First</a>')
        assert len(parser.get_links()) == 1

        parser.reset()

        new_parser = LinkParser("https://example.com")
        new_parser.feed('<a href="/second">Second</a>')
        links = new_parser.get_links()
        assert len(links) == 1
        assert links[0]["url"] == "https://example.com/second"

    def test_malformed_html(self):
        """Test parser resilience with malformed HTML."""
        parser = LinkParser("https://example.com")
        malformed_html = """
        <html>
        <body>
            <a href="/page1.html">Unclosed tag
            <p>Some text
            <a href="/page2.html" title="Page 2">Page 2</a>
        </body>
        """
        parser.feed(malformed_html)
        links = parser.get_links()

        assert len(links) == 2
        assert links[0]["url"] == "https://example.com/page1.html"
        assert links[1]["url"] == "https://example.com/page2.html"
        assert links[1]["title"] == "Page 2"
