import json
import os
import sys

from product_scraper import ProductScraper, FlowerCategory


def main():
    start_page_number = 0
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r") as file:
            checkpoint = json.load(file)
        start_page_number = checkpoint["page_number"]

    categories = [
        FlowerCategory.ROSE,
        FlowerCategory.DAILY_DEALS,
        FlowerCategory.LILY,
        FlowerCategory.SUNFLOWER
    ]

    scraper = ProductScraper()

    try:
        scraper.scrape_products(categories, start_page_number)

    except RuntimeError as e:
        if "RESTART_REQUIRED" in str(e):
            print("Restarting script after checkpoint")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            raise

if __name__ == "__main__":
    main()