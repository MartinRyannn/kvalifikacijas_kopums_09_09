import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import threading

df = pd.DataFrame(columns=["Date", "Price"])

csv_data_window = Tk()
csv_data_window.title("Live Price Chart")
csv_data_window.geometry("1000x600")

plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], 'wo-', markersize=8, linewidth=1)
ax.set_xlim(0, 10)
ax.set_ylim(0, 2500)
ax.set_xlabel('Time')
ax.set_ylabel('Price')
ax.set_title('Live Price Chart')
canvas = FigureCanvasTkAgg(fig, master=csv_data_window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, csv_data_window)
toolbar.update()
canvas.get_tk_widget().pack()

def save_price_to_csv(price):
    current_time = datetime.now()
    new_data = {
        'Date': current_time,
        'Price': price
    }
    df.loc[len(df)] = new_data
    df.to_csv('gold_price.csv', index=False)

def fetch_price():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    url = 'https://www.tradingview.com/symbols/XAUUSD/'
    driver.get(url)

    try:
        while True:
            span_element = driver.find_element(By.CLASS_NAME, 'last-JWoJqCpY')
            price = float(span_element.text.replace(',', ''))
            print("Price:", price)
            save_price_to_csv(price)
            update_chart(price)
            time.sleep(1)
    except Exception as e:
        print("An error occurred while retrieving the price:", e)
    finally:
        driver.quit()

def update_chart(price):
    x = range(len(df))
    line.set_data(x, df['Price'])
    ax.relim()
    ax.autoscale_view()
    ax.set_xlim(max(0, len(df) - 60), len(df))
    ax.set_ylim(price - 0.4, price + 0.4)
    canvas.draw()

threading.Thread(target=fetch_price, daemon=True).start()
csv_data_window.mainloop()
