import json
from datetime import datetime
from enum import Enum

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class FlowerCategory(Enum):
    ROSE = 557
    CARNATION = 453

class ProductScraper:
    def __init__(self):
        self.url = None
        self.driver = None
        self.headers = None
        self.payload = None

    def _init_driver(self):
        # Configure and start Selenium in headless mode.

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = webdriver.Chrome(options=options)

    def _capture_api_request(self):
        self.driver.get("https://www.farm2florist.com")

        ### NAVIGATE TO ROSES PAGE ###
        wait = WebDriverWait(self.driver, 100)
        closePopupButton = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-close"))
        )
        closePopupButton.click()

        roseButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/wholesale-flowers/all-flowers/Roses.html"]')) # todo: find new way to navigate to desired page
        )
        roseButton.click()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div[2]/div[3]/div[2]/div/div/div[1]/div[2]")) # fixme: avoid using hardcoded xpath
        )
        ### NAVIGATED TO ROSES PAGE

        logs = self.driver.get_log('performance')

        for log in logs:
            message = json.loads(log["message"])["message"]
            if message["method"] == "Network.requestWillBeSent":
                req = message["params"]["request"]
                if req["method"] == "POST" and "products/list" in req["url"]:
                    self.url = req["url"]
                    self.headers = req.get("headers", {})
                    self.payload = json.loads(req.get("postData", "{}"))
                    break

        self.headers["Origin"] = "https://www.farm2florist.com"

    def _fetch_api_data(self):
        # Send POST requests to API and compile list of JSON objects to parse
        result = []

        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)

        data = json.loads(response.text)
        num_products = data["products"]["product_count"]
        print("num_products:", num_products)

        num_products = 2 # TODO: REMOVE THIS, IT IS FOR TESTING

        for _ in range(num_products):
            response = requests.post(self.url, headers=self.headers, json=self.payload)

            if response.status_code != 200:
                print("Error:", response.status_code, response.text)
                break

            self.payload["pageNo"] += 1

            data = json.loads(response.text)

            for listingWrapper in data["products"]["result"]:
                result.append((list(listingWrapper.values())[0], data["products"]["cat_name"]))

        return result

    def _parse_products(self, data: list) -> list[dict]:
        # Convert raw JSON into list of structured product dicts.

        result = []

        for x in data:
            listing = x[0]
            category = x[1]

            shipping_date = datetime.strptime(listing["delivery"][0]["delivery_date"], "%d-%b-%Y")
            now = datetime.now()
            shipping_time_hours = (shipping_date - now).total_seconds() / 3600

            entry = {
                "Identifier": listing["info"]["name"],
                "Cost": float(listing["delivery"][0]["perboxprice"].replace("$", "")),
                "Type": category,
                "Color": -1,
                "Number of Flowers per Package": listing["delivery"][0]["qty_per_box"],
                "Stem Length": -1,
                "Shipping Time (Hours)": shipping_time_hours,
            }

            result.append(entry)

        return result

    def scrape_products(self, category: FlowerCategory) -> list[dict]:
        if self.driver is None:
            self._init_driver()

        if self.url is None:
            self._capture_api_request()

        self.payload["category"] = str(category.value)

        api_data = self._fetch_api_data()
        return self._parse_products(api_data)

    def _close(self):
        pass