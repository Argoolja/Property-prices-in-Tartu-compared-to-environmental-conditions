from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import csv
import time


geckodriver_path = "geckodriver.exe"

firefox_binary_path = "C:/Program Files/Mozilla Firefox/firefox.exe"

options = webdriver.FirefoxOptions()
options.binary_location = firefox_binary_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/115.0")

service = Service(geckodriver_path)

driver = webdriver.Firefox(service=service, options=options)

base_url = "https://www.kv.ee/kinnisvara/korterid?county=12&parish=1063&city[0]=4820&city[1]=5708&city[2]=5706&city[3]=5707&city[4]=5704&city[5]=5705&city[6]=5702&city[7]=5703&city[8]=5717&city[9]=5718&city[10]=5715&city[11]=5716&city[12]=5713&city[13]=5714&city[14]=5711&city[15]=5712&city[16]=5709&city[17]=5710&limit=50&start={}"

data = []
index = 1

total_pages = 19
for page in range(0, total_pages):
    print(f"Scraping page {page+1}...")
    url = base_url.format(page*50)
    driver.get(url)

    time.sleep(5)

    articles = driver.find_elements(By.TAG_NAME, "article")

    for article in articles:
        try:
            address = article.find_element(By.CLASS_NAME, "description").text.split("\n")[0].strip()

            if address[0].isdigit():
                address = address[1:].strip()
            
            rooms = article.find_element(By.CLASS_NAME, "rooms").text.strip()
            
            size = article.find_element(By.CLASS_NAME, "area").text.strip()
            
            price = article.find_element(By.CLASS_NAME, "price").text.split("\n")[0].strip()
            
            data.append([index, address, rooms, size, price])
            index += 1
        except Exception as e:
            print(f"Error extracting article: {e}")
            continue

driver.quit()

csv_file = "data/kv_listings.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Index", "Address", "Room Count", "Size", "Price"])
    writer.writerows(data)

print(f"Data has been saved to {csv_file}")