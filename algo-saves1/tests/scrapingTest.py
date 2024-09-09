import pandas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    url = 'https://www.tradingview.com/symbols/XAUUSD/'
    driver.get(url)

    scraped_data = [] 
    
    try:
        while True:
            span_element = driver.find_element(By.CLASS_NAME, 'last-JWoJqCpY')
            price = span_element.text
            current_time = datetime.now()
            data = {'Price': price}
            scraped_data.append(data)
            print("Array:", scraped_data)
            time.sleep(1)
    except Exception as e:
        print("An error occurred while retrieving the price:", e)

    driver.quit()

if __name__ == "__main__":
    main()
