"""Module for scraping website data."""

import argparse
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin


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

    parser.add_argument(
        "--process",
        help="Processing mode: 'single' or 'multi'",
        type=str,
        choices=["single", "multi"],
        required=True,
    )

    # Add --output argument
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


def scrape_images(url, output_dir, use_stdout):
    """Scrape images and print URLs or save files."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    if use_stdout:
        """Print image URLs to CLI"""
        print("\n=== IMAGE URLs ===")
        for img in img_tags:
            img_url = urljoin(url, img.get('src', ''))
            print(img_url)
    else:
        if not output_dir:
            output_dir = "./output"
        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        for img in img_tags:
            img_url = urljoin(url, img.get('src', ''))
            if not img_url:
                continue

            try:
                img_data = requests.get(img_url, stream=True, timeout=10)
                img_data.raise_for_status()
                filename = os.path.basename(img_url)
                filepath = os.path.join(img_dir, filename)
                with open(filepath, 'wb') as f:
                    for chunk in img_data.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")


def main():
    """Execute the main scraping workflow based on command-line arguments."""
    args = parse_args()
    print(f"Scraping URL: {args.url}")
    print(f"Scraping type: {args.type}")
    print(f"Processing mode: {args.process}")

    if args.type == "text":
        scrape_text(args.url, args.output, args.stdout)
    elif args.type == "image":
        scrape_images(args.url, args.output, args.stdout)

    if args.process == "single":
        print("Processing in single mode...")
    elif args.process == "multi":
        print("Processing in multi mode...")


if __name__ == "__main__":
    main()
