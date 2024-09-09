import pandas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

def support_scrape():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    url = 'https://www.tradingview.com/symbols/XAUUSD/technicals/'
    driver.get(url)
    
    scraped_supports = []
    
    try:
        while True:
            span_element = driver.find_element(By.CLASS_NAME, '')