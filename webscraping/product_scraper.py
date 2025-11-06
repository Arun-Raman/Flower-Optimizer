import json
import random
import re
import time
from datetime import datetime
from enum import Enum

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
    def __init__(self):
        self.url = None
        self.headers = None
        self.payload = None

    # Collects and sets the necessary HTTP headers needed to call the f2f API
    def _get_api_headers(self):
        print("Getting API headers")

        kip_url = "https://www.farm2florist.com/env.js"
        response = requests.get(kip_url)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            raise Exception

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
        }

        response = requests.post(x_access_token_url, headers=headers)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            raise Exception

        response_json = json.loads(response.text)
        headers["x-access-token"] = response_json["guest"]["api_token"]
        self.url = "https://www.farm2florist.com/r/api/b2b/farm2florist-admin-bff/admin-bff/products/list"

        # Initialize the request body
        self.payload = json.loads("""
            {
                "category": "",
                "color": "",
                "currencyCode": "USD",
                "farm": "",
                "maxPrice": "",
                "maxWOMargin": "",
                "method": "",
                "minPrice": "",
                "minWOMargin": "",
                "pageNo": 0,
                "q": "",
                "searchEndDate": "",
                "searchStartDate": "",
                "sort": "index",
                "storeId": "28071",
                "variety": ""
            }
        """)
        self.headers = headers

        print("Successfully captured API headers")

    # Sends POST requests to the farm2florist API and compiles a list of JSON objects to parse
    # Returns a list of tuple values where the first element is the JSON object and the second is the product category
    def _fetch_api_data(self):
        print("Fetching API Data")

        result = []

        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)

        data = json.loads(response.text)
        num_products = data["products"]["product_count"]
        print("Total Products:", num_products)

        # num_products = 10 # REMOVE THIS, IT IS FOR TESTING

        while True:
            try:
                response = requests.post(self.url, headers=self.headers, json=self.payload)
            except requests.RequestException as e:
                print("Request error:", e)
                print("Getting new API headers")
                self._get_api_headers()
                continue

            if response.status_code != 200:
                print("Error:", response.status_code, response.text)
                print("Getting new API headers")
                self._get_api_headers()
                continue  # retry same pageNo

            data = response.json()
            products = data.get("products", {})

            if not products or products.get("product_count", 0) == 0:
                break

            for listingWrapper in products.get("result", []):
                result.append((list(listingWrapper.values())[0], products.get("cat_name", "")))

            print(f"{len(result)} products found ({len(result) * 100 / num_products:.2f} %) [pageNo: {self.payload['pageNo']}]")

            self.payload["pageNo"] += 1  # only increment after success

        print("Finished Fetching API Data")

        return result

    # Converts the raw data + product categories to a list of dictionaries in the format needed for the optimizer
    def _parse_products(self, data: list) -> list[dict]:
        print("Parsing Products")

        result = []

        for x in data:
            listing = x[0]
            category = x[1]

            info = listing.get("info", {})
            name = info.get("name", "").strip()

            color = info.get("color", "Unknown").capitalize()
            if color == "Unknown":
                '''base_colors = ["Red", "Pink", "White", "Yellow", "Orange", "Purple", "Blue", "Green",
                               "Cream", "Peach", "Coral", "Lavender", "Magenta", "Violet",
                               "Burgundy", "Maroon", "Gold", "Silver", "Black", "Brown", "Burgundy"]

                # optional
                modifiers = ["Light", "Dark", "Hot", "Soft", "Pale", "Deep", "Bright", "Pastel", "Creamy"]

                # modifiers combined with base colors
                compound_colors = [f"{m} {c}" for m, c in itertools.product(modifiers, base_colors)]

                colors = base_colors + compound_colors + [
                    # common special descriptors
                    "Mixed", "Bi Color", "Two Tone", "Multi Color", "Variegated",
                    "Blush", "Ivory", "Champagne", "Apricot", "Salmon", "Mauve",
                    "Lilac", "Plum", "Wine", "Bronze", "Copper", "Dusty Rose",
                    "Fuchsia", "Teal", "Mint", "Sky Blue", "Navy Blue",
                    "Tangerine", "Canary Yellow", "Lemon Yellow", "Mustard",
                    "Rust", "Terracotta", "Creamy White", "Off White", "Snow White"]

                pattern = r"\b(" + "|".join(colors) + r")\b"'''
                colors = ['blue', 'red', 'pink', 'white', 'purple', 'orange', 'yellow']
                pattern = r"\b(" + "|".join(colors) + r")\b"
                match = re.findall(pattern, name, re.IGNORECASE)
                if match:
                    color = [m for m in match]

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
                "Type": category,
                "Color": color,
                "Number of Flowers per Package": listing["delivery"][0]["qty_per_box"],
                "Stem Length": stem_length,
                "Shipping Time (Hours)": shipping_time_hours,
            }

            result.append(entry)

        print("Finished Parsing Products")

        return result

    # Public function which returns the list of dictionaries representing product listings
    def scrape_products(self, category: FlowerCategory) -> list[dict]:
        # if self.driver is None:
        #     self._init_driver()

        self._get_api_headers()

        self.payload["category"] = str(category.value) # Sets the flower type based on enum values (farm2florist API uses numerical codes to represent flower categories)
        print(f"Scraping category {category.value}")

        api_data = self._fetch_api_data()
        return self._parse_products(api_data)