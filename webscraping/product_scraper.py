import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

import requests

from product_parser import ProductParser


# Enum which holds flower categories as numerical codes used in the f2f API
class FlowerCategory(Enum):
    ROSE = "557"
    DAISY = "477"
    SUNFLOWER = "575"
    LILY = "688_691"
    CARNATION = "453"
    ALSTROMERIA = "431"
    HYDRANGEA = "509"
    POMPON = "552_700_699_698_791_841_750"
    TULIP = "582"
    DAILY_DEALS = "806"

# Class for scraping product listings from Farm2Florist
class ProductScraper:
    MAX_PAGE_RETRIES = 3

    def __init__(self):
        self.session = requests.Session()
        self.url = None
        self.headers = None
        self.payload = None

        self.product_parser = ProductParser()

    # Collects and sets the necessary HTTP headers needed to call the f2f API
    def _get_api_headers(self):
        print("Getting API headers")

        kip_url = "https://www.farm2florist.com/env.js"

        try:
            response = self.session.get(kip_url)
            response.raise_for_status()
            if response.status_code != 200:
                print("Error:", response.status_code, response.text)
                raise Exception
        except Exception:
            print("Retrying...")

            time.sleep(random.uniform(0.5, 1.5))
            self._get_api_headers()

        match = re.search(r'REACT_APP_KIP_KEY\s*[:=]\s*"([^"]+)"', response.text)
        if not match:
            print("Error: could not find REACT_APP_KIP_KEY in response.text")
            raise Exception
        kip_key = match.group(1)

        x_access_token_url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/header" # URL which gives us x-access-token

        # Kip-Apikey does not become invalid so we can just set it to a known functional key
        # Origin has to be farm2florist; otherwise it crashes
        headers = {
            "Kip-Apikey": kip_key,
            "Origin": "https://www.farm2florist.com",
            "Connection": "close"
        }

        response = self.session.post(x_access_token_url, headers=headers)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            raise Exception

        response_json = json.loads(response.text)
        headers["x-access-token"] = response_json["guest"]["api_token"]
        self.url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/products/list"
        self.headers = headers

        print("Successfully captured API headers")

    # Sends POST requests to the farm2florist API and compiles a list of JSON objects to parse
    # Returns a list of tuple values where the first element is the JSON object and the second is the product category
    def _fetch_api_data(self):
        print("Fetching API Data")

        response = self.session.post(self.url, headers=self.headers, json=self.payload)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)

        data = response.json()
        num_products = data["products"]["product_count"]
        print("Total Products:", num_products)

        result = self._fetch_all_pages(self.url, self.headers, self.payload, 0, num_products // 12) # todo: get rid of magic number (12)
        print(f"Result length: {len(result)}")
        print("Finished Fetching API Data")

        return result

    def _fetch_all_pages(self, url, headers, payload_template, start_page, end_page):
        pending = {p: 0 for p in range(start_page, end_page + 1)}
        result = []

        with ThreadPoolExecutor(max_workers=16) as ex:
            session = requests.Session()

            def submit_page(page):
                return ex.submit(self._fetch_page, session, url, headers, payload_template, page), page

            future_map = dict(submit_page(p) for p in pending)

            while future_map:
                for future in as_completed(future_map):
                    page = future_map.pop(future)
                    try:
                        data = future.result()
                        products = data.get("products", {})
                        for listingWrapper in products.get("result", []):
                            listing = list(listingWrapper.values())[0]
                            listing["category"] = products.get("cat_name", "NA")

                            result.append(listing)

                    except Exception as e:
                        print(f"Page {page} failed: \"{e}\"")

                        retries = pending[page] + 1
                        if retries > self.MAX_PAGE_RETRIES:
                            print(f"Page {page} exhausted retries: \"{e}\"")
                            continue
                        pending[page] = retries
                        time.sleep(1 * retries)
                        fut_new, page_new = submit_page(page)
                        future_map[fut_new] = page_new

        return result

    def _fetch_page(self, session, url, headers, payload_template, page_no):
        # print(f"Fetching Page {page_no}")

        payload = payload_template.copy()
        payload["pageNo"] = page_no

        resp = session.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _checkpoint_and_restart(self):
        print("Checkpointing for restart")

        checkpoint = {
            "page_number": self.payload["pageNo"]
        }

        with open("checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=2)

        raise RuntimeError("RESTART_REQUIRED")

    def _write_csv(self, data, filename="products.csv"):
        import csv, os
        fieldnames = [
            "Identifier", "Cost", "Type", "Color", "Color Category", "Color Listed",
            "Number of Flowers per Package", "Stem Length", "Shipping Time (Hours)"
        ]
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        write_header = not os.path.exists(filepath)
        with open(filepath, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(data)
        print(f"Data written to {filename}")

    # Public function which returns the list of dictionaries representing product listings
    def scrape_products(self, categories: list[FlowerCategory], from_page_no: int = 0):
        self._get_api_headers()

        category_str = "_".join([category.value for category in categories]).strip("_")

        print(f"Scraping category: {category_str}")

        self.payload = {
            "category": category_str,
            "pageNo": from_page_no,
            "color": "",
            "currencyCode": "USD",
            "farm": "",
            "maxPrice": "",
            "maxWOMargin": "",
            "method": "",
            "minPrice": "",
            "minWOMargin": "",
            "q": "",
            "searchEndDate": "",
            "searchStartDate": "",
            "sort": "index",
            "storeId": "28071",
            "variety": ""
        }

        api_data = self._fetch_api_data()
        self._write_csv(self.product_parser.parse_products(api_data))