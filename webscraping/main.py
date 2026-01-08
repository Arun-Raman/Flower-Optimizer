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
        FlowerCategory.ROSES,
        FlowerCategory.ROSE_FREEDOM,
        FlowerCategory.DAVID_AUSTIN_GARDEN_ROSE,
        FlowerCategory.ROSE_BICOLOR,
        FlowerCategory.SPRAY_ROSE_1,
        FlowerCategory.SPRAY_ROSE_2,
        FlowerCategory.SPRAY_ROSE_GARDEN,
        FlowerCategory.DAISY,
        FlowerCategory.GERBERAS_DAISY,
        FlowerCategory.SUNFLOWER,
        FlowerCategory.LILIES,
        FlowerCategory.LILY_ASIATIC,
        FlowerCategory.LILY_ORIENTAL,
        FlowerCategory.CARNATION,
        FlowerCategory.ALSTROMERIA,
        FlowerCategory.HYDRANGEA,
        FlowerCategory.POMPONS,
        FlowerCategory.POMPON_BUTTON,
        FlowerCategory.POMPON_CDN,
        FlowerCategory.POMPON_CUSHION,
        FlowerCategory.POMPON_DAISY,
        FlowerCategory.POMPON_NOVELTY,
        FlowerCategory.TULIP,
        FlowerCategory.DAILY_DEALS,
    ]

    scraper = ProductScraper()

    try:
        for category in categories:
            scraper.scrape_products([category], start_page_number)

    except RuntimeError as e:
        if "RESTART_REQUIRED" in str(e):
            print("Restarting script after checkpoint")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            raise

if __name__ == "__main__":
    main()