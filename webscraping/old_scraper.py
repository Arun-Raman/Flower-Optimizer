import csv
import json
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Set options for headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
driver = webdriver.Chrome(options=options)

driver.get("https://www.farm2florist.com")

### NAVIGATE TO ROSES PAGE ###
wait = WebDriverWait(driver, 10)
closePopupButton = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-close"))
)
closePopupButton.click()

wait = WebDriverWait(driver, 10)
roseButton = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/wholesale-flowers/all-flowers/Roses.html"]'))    # todo: find new way to navigate to desired page
)
roseButton.click()

wait = WebDriverWait(driver, 10)
roseListingsParent = wait.until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div[2]/div[3]/div[2]/div/div/div[1]/div[2]"))  # fixme: avoid using hardcoded xpath
)
### NAVIGATED TO ROSES PAGE

logs = driver.get_log('performance')

url, headers, payload = None, {}, None
for log in logs:
    message = json.loads(log["message"])["message"]
    if message["method"] == "Network.requestWillBeSent":
        req = message["params"]["request"]
        if req["method"] == "POST" and "products/list" in req["url"]:
            url = req["url"]
            headers = req.get("headers", {})
            payload = json.loads(req.get("postData", "{}"))
            break

driver.quit()   # Driver no longer needed; we have the HTTP headers needed to directly call the API now

# print("Captured:", url, headers, payload, sep="\n")
headers["Origin"] = "https://www.farm2florist.com"

with open("../roses.csv", "w", newline='') as csvfile:  # Initialize CSV file with column names
    writer = csv.writer(csvfile)
    writer.writerow(['Category', 'Product Name', 'Vendor', 'Per Box Price', 'Quantity per Box', 'Delivery Date', 'Stems Available'])    # todo: add more columns available in data

while True: # fixme: Should not be using an infinite loop; only for demonstration
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        break

    payload["pageNo"] += 1  # Increment page number

    jsonString = response.text
    data = json.loads(jsonString)   # fixme: wrap following code in try/except for safety
    for listingWrapper in data["products"]["result"]:
        listing = list(listingWrapper.values())[0]  # Needed because listingWrapper is a map which holds a single value inside it for some reason

        # print(listing["info"]["name"])

        # Each listing has relevant data under either "info" or "delivery
        # The easiest way to get a specific field value I've found is to use dev tools in your browser to peek at the JSON structure of the POST request in network traffic

        with open("../roses.csv", "a", newline='') as csvfile:  # Write rows from this request to roses.csv
            writer = csv.writer(csvfile)
            writer.writerow([
                data["products"]["cat_name"],
                listing["info"]["name"],
                listing["info"]["vendor"],
                listing["delivery"][0]["perboxprice"],
                listing["delivery"][0]["qty_per_box"],
                listing["delivery"][0]["delivery_date"],
                listing["delivery"][0]["floorallowed"],
            ])

            csvfile.flush() # Ensure changes are written to disk