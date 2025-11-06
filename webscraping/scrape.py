import os

from product_scraper import ProductScraper
from product_scraper import FlowerCategory

import csv


scraper = ProductScraper()
# data = (scraper.scrape_products(FlowerCategory.DAILY_DEALS) +
#         scraper.scrape_products(FlowerCategory.ROSE) +
#         scraper.scrape_products(FlowerCategory.SUNFLOWER)
# )

data = scraper.scrape_products(FlowerCategory.DAILY_DEALS)

fieldnames = ["Identifier", "Cost", "Type", "Color", "Number of Flowers per Package", "Stem Length", "Shipping Time (Hours)"]

output_dir = "data"
output_filename = "products.csv"

with open(os.path.join(output_dir, output_filename), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(data)

print(f"Data successfully written to {output_filename}")