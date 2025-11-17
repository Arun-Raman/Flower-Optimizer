import json
import random
import re
import time
import colorsys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from enum import Enum
from matplotlib import colors
from transformers import pipeline

import requests


# Enum which holds flower categories as numerical codes used in the f2f API
class FlowerCategory(Enum):
    ROSE = "557"
    SUNFLOWER = "575"
    LILY = "688_691"
    CARNATION = "453"
    DAILY_DEALS = "806"

# Class for scraping product listings from Farm2Florist
class ProductScraper:
    MAX_PAGE_RETRIES = 3

    def __init__(self):
        self.session = requests.Session()
        self.url = None
        self.headers = None
        self.payload = None

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

        result = []

        response = self.session.post(self.url, headers=self.headers, json=self.payload)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)

        data = response.json()
        num_products = data["products"]["product_count"]
        print("Total Products:", num_products)

        result = self._fetch_all_pages(self.url, self.headers, self.payload, 0, num_products // 12) # todo: get rid of magic number (12)
        print(f"Result length: {len(result)}")

        # consecutive_failed_requests = 0
        # while True:
        #     if consecutive_failed_requests > 3:
        #         print("Error: too many failed requests")
        #         self._write_csv(self._parse_products(result))
        #         self._checkpoint_and_restart()
        #
        #     response = self.session.post(self.url, headers=self.headers, json=self.payload)
        #
        #     if response.status_code != 200:
        #         consecutive_failed_requests += 1
        #
        #         print("Error:", response.status_code, response.text)
        #
        #         wait = consecutive_failed_requests * 2 + random.uniform(0, 3)
        #         print(f"Waiting {wait:.2f} seconds before retrying...")
        #         time.sleep(wait)
        #         #
        #         # print("Refreshing API headers")
        #         # self._get_api_headers()
        #         continue  # retry same pageNo
        #
        #     try:
        #         data = response.json()
        #     except json.JSONDecodeError:
        #         print("Error: received invalid JSON (possibly HTML error page). Retrying...")
        #         consecutive_failed_requests += 1
        #         wait = consecutive_failed_requests * 2 + random.uniform(0, 3)
        #         print(f"Waiting {wait:.2f} seconds before retrying...")
        #         time.sleep(wait)
        #         print("Refreshing API headers")
        #         self._get_api_headers()
        #         continue
        #
        #     consecutive_failed_requests = 0
        #
        #     products = data.get("products", {})
        #     num_products = data["products"]["product_count"]
        #
        #     if not products or products.get("product_count", 0) == 0:
        #         break
        #
        #     for listingWrapper in products.get("result", []):
        #         result.append((list(listingWrapper.values())[0], products.get("cat_name", "")))
        #
        #     print(f"{len(result)} products found ({len(result) * 100 / num_products:.2f} %) [pageNo: {self.payload['pageNo']}]")
        #     self.payload["pageNo"] += 1
        #
        #     time.sleep(random.uniform(0.5, 1.5))

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
                            result.append((list(listingWrapper.values())[0], products.get("cat_name", "NA"))) # todo: find better way to set category

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
        print(f"Fetching Page {page_no}")

        payload = payload_template.copy()
        payload["pageNo"] = page_no

        resp = session.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()

    # Converts the raw data + product categories to a list of dictionaries in the format needed for the optimizer
    def _parse_products(self, data: list) -> list[dict]:
        print("Parsing Products")

        result = []
        # classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli") # embeddings model

        # gets list of ~950 matlab colors for extracting colors from listing name
        colors_categorized = {'red': [], 'orange': [], 'yellow': [], 'green': [], 'blue': [], 'purple': [], 'pink': [], 'white': [], 'other': []}
        all_colors = colors.get_named_colors_mapping()
        for name, val in all_colors.items():
            r, g, b = colors.to_rgb(val)
            h, s, v = colorsys.rgb_to_hsv(r, g, b)

            if s < 0.2 and v > 0.8:
                colors_categorized['white'].append(name)

            if 0.0 <= h < 0.05:
                colors_categorized['red'].append(name)
            elif 0.05 <= h < 0.15:
                colors_categorized['orange'].append(name)
            elif 0.15 <= h < 0.25:
                colors_categorized['yellow'].append(name)
            elif 0.25 <= h < 0.45:
                colors_categorized['green'].append(name)
            elif 0.45 <= h < 0.65:
                colors_categorized['blue'].append(name)
            elif 0.65 <= h < 0.85:
                colors_categorized['purple'].append(name)
            elif 0.85 <= h < 1.0:
                colors_categorized['pink'].append(name)
            else:
                colors_categorized['other'].append(name)

        flat_colors = []
        for cat, color_list in colors_categorized.items():
            flat_colors.append(cat)
            for c in color_list:
                flat_colors.append(c)
        pattern = r'\b(' + '|'.join(re.escape(c) for c in flat_colors) + r')\b'
        color_regex = re.compile(pattern, re.IGNORECASE)

        for x in data:
            listing = x[0]
            flower_category = x[1]

            info = listing.get("info", {})
            name = str(info.get("name", "").strip())

            color_cat = 'placeholder'
            color = info.get("color", "Unknown").capitalize()
            color_listed = True

            if "sunf" in name.lower(): # sunflowers are yellow
                if color == "Unknown":
                    color_listed = False
                    color = color_cat = "yellow"
            else:
                if "coral" in name.lower():
                    color_listed = False
                    color = color_cat = "pink"
                elif "ros ylw" in name.lower(): # these are NOT yellow and embeddings mistakenly makes some red
                    color_listed = False
                else:
                    match = color_regex.search(name.lower())
                    if match:
                        if color == 'Unknown':
                            color = match.group(1)
                            color_listed = False
                        for cat, color_list in colors_categorized.items():
                            if color in color_list:
                                color_cat = cat
                    else: # use embeddings model
                        continue
                        print("======================================================================")
                        print("Using embeddings model:", name)
                        labels = ["red", "pink", "yellow", "white", "purple", "blue", "orange", "green"]
                        embresult = classifier(name.lower(), labels)

                        print("confidence:", embresult["scores"][0])
                        if embresult["scores"][0] > 0.5: # high confidence
                            color = embresult["labels"][0]
                            color_cat = color
                            print("color:", color)
                        print("======================================================================")

            stem_length = info.get("length", 0)
            if isinstance(stem_length, str) and stem_length.isdigit():
                stem_length = int(stem_length)
            if not isinstance(stem_length, int) or stem_length == 0:
                match = re.search(r"\d+", name)
                if match:
                    stem_length = int(match.group())
                else:
                    stem_length = 0

            shipping_date = datetime.strptime(listing["delivery"][0]["delivery_date"], "%d-%b-%Y")
            now = datetime.now()
            shipping_time_hours = (shipping_date - now).total_seconds() / 3600

            entry = {
                "Identifier": listing["info"]["name"],
                "Cost": float(listing["delivery"][0]["perboxprice"].replace("$", "")),
                "Type": flower_category,
                "Color": color,
                "Color Category": color_cat,
                "Color Listed": color_listed,
                "Number of Flowers per Package": listing["delivery"][0]["qty_per_box"],
                "Stem Length": stem_length,
                "Shipping Time (Hours)": shipping_time_hours,
            }

            result.append(entry)

        print("Finished Parsing Products")

        return result

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
        self._write_csv(self._parse_products(api_data))