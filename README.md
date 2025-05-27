# Chuchu-Scrapper

## Description
A powerful and flexible web scraping tool built in Python that extracts text, images, and links from websites. The scraper provides a command-line interface for easy data extraction and supports multiple output formats.

## Features
- 🌐 Text extraction from web pages
- 🖼️ Image downloading capabilities
- 🔗 Link extraction and reporting
- 📝 Multiple parser types (TextParser, ImageParser, LinkParser)
- 💾 Flexible output formats
- ⚡ Command-line interface
- ✅ Comprehensive test coverage

## Requirements
- Python 3.9 or higher
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Egbewattnkongho13/chuchu-scrapper.git
cd chuchu-scrapper
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

### Basic Usage
```bash
poetry run main <url> --type <text|images|links> [--output <filepath>] [--stdout]
```

### Options
- `--type`: Specify the type of content to scrape (required)
  - `text`: Extract text content
  - `images`: Download images
  - `links`: Extract links
- `--output`: Save output to a file (optional)
- `--stdout`: Print output to console (optional)

### Examples
Extract text from a webpage and print to console:
```bash
poetry run main https://example.com --type text --stdout
```

Download images from a webpage to a specific folder:
```bash
poetry run main https://example.com --type images --output ./downloaded_images
```

Extract links and save to a file:
```bash
poetry run main https://example.com --type links --output links.txt
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Style
The project uses pre-commit hooks for code formatting and linting. To set up:
```bash
poetry run pre-commit install
```


## Project Structure
```
chuchu-scrapper/
├── src/
│   └── chuchu_scrapper/
│       ├── __init__.py
│       ├── main.py
│       ├── cli.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── text_parser.py
│       │   ├── image_parser.py
│       │   └── link_parser.py
│       └── utils/
│           ├── __init__.py
│           ├── scraper.py
│           └── io.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_cli.py
│   ├── data/
│   │   └── sample.html
│   ├── test_parsers/
│   │   ├── __init__.py
│   │   ├── test_text_parser.py
│   │   ├── test_image_parser.py
│   │   └── test_link_parser.py
│   └── test_utils/
│       ├── __init__.py
│       ├── test_scraper.py
│       └── test_io.py
├── pyproject.toml
├── poetry.lock
├── .gitignore
├── README.md
└── CHANGELOG.md
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
