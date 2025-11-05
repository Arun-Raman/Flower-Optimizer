import json
import random
import re
import time
from datetime import datetime
from enum import Enum

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        self.driver = None
        self.headers = None
        self.payload = None

    # Initializes the driver and sets options for headless mode + enabling access to network logs
    def _init_driver(self):
        print("Initializing Selenium Webdriver")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = webdriver.Chrome(options=options)

        print("Finished Initializing Selenium Webdriver")

    # Navigates to a flower listing page (the roses page is used here), and captures HTTP request headers+payload needed to send API requests directly
    def _capture_api_request(self):
        print("Capturing API Request")

        self.driver.get("https://www.farm2florist.com/wholesale-flowers/all-flowers/Roses.html") # Navigate directly to the roses page
        found_headers = False
        while True: # Checks logs every 1 second to check if needed API keys are present yet
            logs = self.driver.get_log('performance')
            for log in logs:
                message = json.loads(log["message"])["message"]
                if message.get("method") == "Network.requestWillBeSent":
                    req = message["params"]["request"]
                    if req["method"] == "POST" and "products/list" in req["url"]:
                        headers = req.get("headers", {})
                        if "Kip-Apikey" in headers and "x-access-token" in headers:
                            self.url = req["url"]
                            self.headers = {
                                "Kip-Apikey": headers["Kip-Apikey"],
                                "x-access-token": headers["x-access-token"]
                            }
                            found_headers = True
                            break
            if found_headers:
                break
            time.sleep(1)

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
        self.headers["Origin"] = "https://www.farm2florist.com" # We need to set the Origin as farm2florist.com; otherwise we get a 503 Error

        print("Finished Capturing API Request")

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
                wait_time = 5 + random.uniform(0, 3)
                print(f"Waiting {wait_time:.2f}s before retrying...")
                time.sleep(wait_time)
                continue

            if response.status_code != 200:
                print("Error:", response.status_code, response.text)
                wait_time = 5 + random.uniform(0, 3)
                print(f"Waiting {wait_time:.2f}s before retrying...")
                time.sleep(wait_time)
                continue  # retry same pageNo

            data = response.json()
            products = data.get("products", {})

            if not products or products.get("product_count", 0) == 0:
                break

            for listingWrapper in products.get("result", []):
                result.append((list(listingWrapper.values())[0], products.get("cat_name", "")))

            print(f"{len(result)} products found ({len(result) * 100 / num_products:.2f} %)")

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
        if self.driver is None:
            self._init_driver()

        if self.url is None:
            self._capture_api_request()

        self.payload["category"] = str(category.value) # Sets the flower type based on enum values (farm2florist API uses numerical codes to represent flower categories)

        api_data = self._fetch_api_data()
        return self._parse_products(api_data)