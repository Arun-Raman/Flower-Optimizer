from product_scraper import ProductScraper
from product_scraper import FlowerCategory

scraper = ProductScraper()
result = scraper.scrape_products(FlowerCategory.CARNATION)

print(result)