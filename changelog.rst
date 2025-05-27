# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-27

### Added
- Initial project setup with Poetry.
- Created `README.md` with project overview and usage instructions.
- Implemented CLI web scraper supporting text and image extraction.
- Added web scraping module with `TextParser`, `ImageParser`, and `LinkParser` classes.
- Added functions for scraping text and images from URLs.
- Implemented comprehensive docstrings for all modules.
- Added sample HTML file for mock testing.
- Added unit tests for:
  - `TextParser`, `ImageParser`, and `LinkParser` classes.
  - Scraper functions: `scrape_text`, `scrape_images`, and related utilities.
  - I/O functions: `save_text`, `save_links`.
  - CLI initialization and fetch functionality.
  - Non-HTML content handling.

### Changed
- Restructured component/module files and updated all import paths to reflect new structure.
- Updated linting configuration and applied pre-commit auto-fixes.

### Fixed
- Fixed import issues after restructuring modules.

### Security
- No known security issues in this release.

---

Older versions will be added as the project evolves.
