import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import csv

# Set options for headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# Begin navigating to roses page
driver.get("https://www.farm2florist.com")

wait = WebDriverWait(driver, 10)
closePopupButton = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-close"))
)
closePopupButton.click()

wait = WebDriverWait(driver, 10)
roseButton = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/wholesale-flowers/all-flowers/Roses.html"]'))
)
roseButton.click()

wait = WebDriverWait(driver, 10)
roseListingsParent = wait.until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div[2]/div[3]/div[2]/div/div/div[1]/div[2]"))
)

# Begin writing data to roses.csv
wait = WebDriverWait(driver, 100000)

with open("../roses.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Category', 'Supplier', 'Price', 'Product Name', 'Quantity', 'Delivery Date', 'Boxes Available'])

numListings = 0
done = False
while not done:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    roseListingsParent = driver.find_element(By.XPATH,
                                       "/html/body/div[1]/div/main/div[2]/div[3]/div[2]/div/div/div[1]/div[2]")

    try:
        wait.until(
            lambda d: len(roseListingsParent.find_elements(By.XPATH, "./*")) != numListings
        )

        child_elements = roseListingsParent.find_elements(By.XPATH, "./*")

        for child in child_elements[numListings:]:
            rawText = child.text
            category = re.search(r'^(.+?)\s*\|', rawText).group(1).strip()
            supplier = re.search(r'\|\s*(.+?)$', rawText.split('\n')[0]).group(1).strip()
            price = re.search(r'\$(\d+\.?\d*)', rawText).group(1)
            product_name = rawText.split('\n')[2].strip()
            quantity = re.search(r'(\d+)\s+(?:Bunches|Stems)', rawText).group(1)
            unit_price = re.search(r'\$(\d+\.?\d*)\s+each', rawText).group(1)
            delivery_date = re.search(r'Get it by (.+)', rawText).group(1).strip()
            boxes_available = re.search(r'(\d+)\s+Boxes Available', rawText).group(1)

            print(category, supplier, price, product_name, quantity, delivery_date, boxes_available)

            with open("../roses.csv", "a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([category, supplier, price, product_name, quantity, delivery_date, boxes_available])
                csvfile.flush()

        numListings = len(roseListingsParent.find_elements(By.XPATH, "./*"))

        # if numListings >= 40: # Temporarily here for demo
        #     done = True

    except TimeoutException:
        print("Timeout error")
        done = True