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
import re

df = pd.DataFrame(columns=["Date", "Price"])

csv_data_window = Tk()
csv_data_window.title("Live Price Chart")

plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(8, 3.8))
line, = ax.plot([], [], 'wo-', markersize=1, alpha=0.7)
ax.set_xlim(0, 10)
ax.set_ylim(0, 100) 
ax.set_xlabel('Time')
ax.set_ylabel('Volume')
ax.set_title('Live Volume Chart')

canvas = FigureCanvasTkAgg(fig, master=csv_data_window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, csv_data_window)
toolbar.update()
canvas.get_tk_widget().pack()

def update_plot(volume):
    global df
    current_time = datetime.now().strftime("%H:%M:%S")
    new_row = pd.DataFrame({"Date": [current_time], "Price": [volume]})
    df = pd.concat([df, new_row], ignore_index=True)
    if len(df) > 10:
        df = df.iloc[1:]
    ax.set_xlim(0, len(df))
    ax.set_ylim(0, df["Price"].max() + 10)
    ax.set_ylim(volume - 1, volume + 1)
    line.set_data(range(len(df)), df["Price"])
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["Date"], rotation=45, ha='right')
    canvas.draw()

def fetch_volume():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    url = 'https://www.tradingview.com/symbols/XAUUSD/'
    driver.get(url)
    
    try:
        while True:
            text_element = driver.find_element(By.CLASS_NAME, 'value-GgmpMpKr')
            volume_text = text_element.get_attribute('innerHTML')
            match = re.search(r'(\d+\.\d+)', volume_text)
            if match:
                volume = float(match.group(1))
                print("Volume:", volume)
                update_plot(volume)
            time.sleep(1)
    except Exception as e:
        print("Error getting the volume:", e)
    finally:
        driver.quit()

threading.Thread(target=fetch_volume, daemon=True).start()

csv_data_window.mainloop()
