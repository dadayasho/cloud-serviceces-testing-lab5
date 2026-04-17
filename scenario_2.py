from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(options=options)

try:
    driver.get("https://youtube.ru")
    time.sleep(8)

    driver.save_screenshot("screenshot.png")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

finally:
    driver.quit()