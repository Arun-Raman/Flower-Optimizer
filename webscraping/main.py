import json
import os
import sys

from product_scraper import ProductScraper, FlowerCategory


def main():
    categories = [
        FlowerCategory.ROSE,
        FlowerCategory.DAILY_DEALS,
        FlowerCategory.LILY,
        FlowerCategory.SUNFLOWER
    ]
    start_page_number = 0

    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r") as file:
            checkpoint = json.load(file)

        last_category = FlowerCategory(checkpoint["category"])
        start_page_number = checkpoint["page_number"]

        # Resume from the saved category and onwards
        if last_category in categories:
            idx = categories.index(last_category)
            categories = categories[idx:]

    scraper = ProductScraper()
    data = []

    try:
        for category in categories:
            data += scraper.scrape_products(category, start_page_number)
            print("\n")
            start_page_number = 0

    except RuntimeError as e:
        if "RESTART_REQUIRED" in str(e):
            print("Restarting script after checkpoint")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            raise

    # # write only if finished successfully
    # fieldnames = [
    #     "Identifier", "Cost", "Type", "Color",
    #     "Number of Flowers per Package", "Stem Length", "Shipping Time (Hours)"
    # ]
    # output_dir = "data"
    # os.makedirs(output_dir, exist_ok=True)
    # output_filename = "products.csv"
    #
    # with open(os.path.join(output_dir, output_filename), 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(data)
    #
    # print(f"Data successfully written to {output_filename}")

if __name__ == "__main__":
    main()