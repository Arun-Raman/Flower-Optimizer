import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

import requests

from product_parser import ProductParser


# Enum which holds flower categories as numerical codes used in the f2f API
class FlowerCategory(Enum):
    ROSES = "557"
    ROSE_FREEDOM = "707"
    DAVID_AUSTIN_GARDEN_ROSE = "701"
    ROSE_BICOLOR = "702"
    DAISY = "477"
    GERBERAS_DAISY = "799"
    POMPON_DAISY = "699"
    SUNFLOWER = "575"
    LILY_ASIATIC = "688"
    LILY_ORIENTAL = "691"
    CARNATION = "453"
    ALSTROMERIA = "431"
    HYDRANGEA = "509"
    POMPONS = "552"
    POMPON_BUTTON = "750"
    POMPON_CDN = "791"
    POMPON_CUSHION = "698"
    POMPON_NOVELTY = "700"
    TULIP = "582"
    DAILY_DEALS = "806"

# Class for scraping product listings from Farm2Florist
class ProductScraper:
    MAX_PAGE_RETRIES = 3
    USE_LOGIN = True

    def __init__(self):
        self.session = requests.Session()
        self.url = None
        self.headers = None
        self.payload = None
        self.store_id = "28071" # Default signed out store id

        self.product_parser = ProductParser()

    # Collects and sets the necessary HTTP headers needed to call the f2f API
    def _get_api_headers(self):
        print("Getting API headers")

        headers = {
            "Origin": "https://www.farm2florist.com",
            "Connection": "close"
        }

        # Get Kip-ApiKey
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

        headers["Kip-Apikey"] = kip_key


        # Get signed out in x-access-token
        x_access_token_url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/header" # URL which gives us x-access-token

        response = self.session.post(x_access_token_url, headers=headers)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            raise

        response_json = json.loads(response.text)
        headers["x-access-token"] = response_json["guest"]["api_token"]

        # Get signed in x-access-token and store id
        if self.USE_LOGIN:
            self._log_in(headers)

        self.url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/products/list"
        self.headers = headers

        print("Successfully captured API headers")

    def _log_in(self, headers):
        login_url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/user/login"

        login_email = os.environ.get("FARM2FLORIST_LOGIN_EMAIL")
        login_password_hashed = os.environ.get("FARM2FLORIST_LOGIN_PASSWORD_HASHED")
        login_random_key = os.environ.get("FARM2FLORIST_LOGIN_RANDOM_KEY")

        response = self.session.post(login_url, headers=headers, json={
            "email": login_email,
            "password": login_password_hashed,
            "random_key": login_random_key
        })
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            raise

        response_json = json.loads(response.text)
        headers["x-access-token"] = response_json[0]["result"]["api_token"]
        self.store_id = response_json[0]["result"]["store_list"][0]["store_id"]

    # Sends POST requests to the farm2florist API and compiles a list of JSON objects to parse
    # Returns a list of tuple values where the first element is the JSON object and the second is the product category
    def _fetch_api_data(self):
        print("Fetching API Data")

        result = self._fetch_all_pages(self.url, self.headers, self.payload)

        print(f"{len(result)} products scraped")
        print("Finished Fetching API Data")

        return result

    def _fetch_all_pages(self, url, headers, payload_template):
        max_workers = 16
        failures = {} # dict mapping page number to num retries
        pages_submitted = {0}
        result = []

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            def submit_page(page):
                return ex.submit(self._fetch_page, self.session, url, headers, payload_template, page), page

            future_map = dict([submit_page(0)])

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

                        total_product_count = products.get("product_count")

                        results_per_page = len(products.get("result", []))
                        total_pages = (total_product_count + results_per_page - 1) // results_per_page
                        if len(pages_submitted) < total_pages:
                            for next_page in range(total_pages):
                                if next_page not in pages_submitted:
                                    fut_new, page_new = submit_page(next_page)
                                    future_map[fut_new] = page_new
                                    pages_submitted.add(next_page)

                    except Exception as e:
                        print(f"Page {page} failed: \"{e}\"")

                        retries = failures.get(page, 0) + 1
                        if retries > self.MAX_PAGE_RETRIES:
                            print(f"Page {page} exhausted retries: \"{e}\"")
                            continue
                        failures[page] = retries
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
            "Identifier", "Cost", "Category", "Color", "Color Category", "Color Listed",
            "Number of Flowers per Package", "Stem Length", "Shipping Date", "Variety", "Vendor"
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

        print(f"\nScraping category: {category_str}")

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
            "storeId": self.store_id,
            "variety": ""
        }

        api_data = self._fetch_api_data()
        self._write_csv(self.product_parser.parse_products(api_data))