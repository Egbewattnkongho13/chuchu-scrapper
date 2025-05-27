"""Main workflow for the ChuChu scraper application."""

import argparse
import os

from chuchu_scrapper.scrapper import ChuChuScrapper


def parse_args():
    """
    Parse command line arguments for the ChuChu scraper application.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.

    The following arguments are supported:
        - url: URL of the website to scrape
        - --output: Directory to save the scraped data (default: ./outputs)
        - --type: Type of data to be scraped (choices: text, image, link, all)
        - --stdout: Flag to print the scraped data to standard output
    """
    parser = argparse.ArgumentParser(
        prog="chuchu_scrapper",
        description="A web scraping tool for collecting information from websites.",
    )
    parser.add_argument("url", type=str, help="URL of the website to scrape")
    parser.add_argument(
        "--output",
        type=str,
        default="./outputs",
        help="Directory to save the scrapped data.",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["text", "image", "link", "all"],
        required=True,
        help="Type of data to be scrapped.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the scrapped data to standard output.",
    )
    return parser.parse_args()


def run():
    """
    Run the ChuChu scraper.

    This function:
    1. Parses command-line arguments
    2. Creates a ChuChuScrapper instance
    3. Executes the appropriate scraping function based on the requested type
    4. Either prints the results to stdout or saves them to files

    Returns:
        None
    """
    args = parse_args()
    chuchu_scrapper = ChuChuScrapper()

    if not args.stdout:
        os.makedirs(args.output, exist_ok=True)

    if args.type == "text":
        text_content = chuchu_scrapper.scrape_text(args.url)
        if args.stdout:
            print("\n=== Scraped Text Content ===\n")
            print(text_content)
        else:
            path = chuchu_scrapper.save_text(text_content, args.output)
            print(f"Text content saved to {path}")

    elif args.type == "image":
        image_content = chuchu_scrapper.scrape_images(args.url)
        if args.stdout:
            print("\n=== Scraped Image Content ===\n")
            print(image_content)
        else:
            chuchu_scrapper.download_images(image_content, args.output)
            print(f"Image content saved to {args.output}")

    elif args.type == "link":
        link_content = chuchu_scrapper.scrape_links(args.url)
        if args.stdout:
            print(chuchu_scrapper.format_links_report(link_content))
        else:
            chuchu_scrapper.save_links(link_content, args.output)
