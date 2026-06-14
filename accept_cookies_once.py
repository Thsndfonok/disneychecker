# accept_cookies_once.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

print("Opening browser...")
driver = webdriver.Chrome()
driver.get("https://www.disneyplus.com")
time.sleep(5)

print("\n👉 MANUALLY click 'Accept' on the cookie popup now")
print("👉 Then press Enter here...")
input()

driver.quit()
print("✅ Cookies accepted! Now run the main script")