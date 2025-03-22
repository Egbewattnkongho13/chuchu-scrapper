"""Module for scraping website data."""

import argparse
from bs4 import BeautifulSoup
import requests
import os


def parse_args():
    """
    Parse command-line arguments for the chuchu-scrapper application.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.

    Args:
        url (str): The URL to scrape. This is a required positional argument.
        --type (str): The type of data to process. Must be one of ["text", "image"].
                      This is a required argument.
        --process (str): The processing mode to use. Must be one of ["single", "multi"].
                         This is a required argument.
    """
    parser = argparse.ArgumentParser(
        prog="chuchu-scrapper", description="A simple CLI scrapper application."
    )

    # Add --url argument
    parser.add_argument("url", help="URL to scrap", type=str)

    # Add --type argument
    parser.add_argument(
        "--type",
        help="Type data to the script",
        type=str,
        choices=["text", "image"],
        required=True,
    )

    # Add --output argument
    parser.add_argument(
        "--process",
        help="Processing mode: 'single' or 'multi'",
        type=str,
        choices=["single", "multi"],
        required=True,
    )

    parser.add_argument(
        "--output",
        help="Directory to save file (optional)",
        type=str
    )

    parser.add_argument(
        "--stdout",
        help="Print results to CLI instead of saving",
        action="store_true"
    )
    return parser.parse_args()


def scrape_text(url, output_dir, use_stdout):
    """Scrape text and print/save it."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    text_content = '\n'.join([e.get_text(strip=True) for e in text_elements])

    if use_stdout:
        """Print directly to CLI"""
        print("\n=== SCRAPED TEXT ===\n")
        print(text_content)
    else:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "scrapped_text.txt")
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            print(f"Text saved to: {output_path}")
        except IOError as e:
            print(f"Error writing file: {e}")


def main():
    """Execute the main scraping workflow based on command-line arguments."""
    args = parse_args()
    print(f"Scraping URL: {args.url}")
    print(f"Scraping type: {args.type}")
    print(f"Processing mode: {args.process}")

    if args.type == "text":
        print(f"Scraping text content from {args.url}...")

    elif args.type == "image":
        print(f"Scraping image content from {args.url}...")

    if args.process == "single":
        print("Processing in single mode...")

    elif args.process == "multi":
        print("Processing in multi mode...")


if __name__ == "__main__":
    main()
