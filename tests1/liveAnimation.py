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
import matplotlib.dates as mdates

# Izveido datu rāmi ar kolonnu nosaukumiem "Date" un "Price"
df = pd.DataFrame(columns=["Date", "Price"])

# Izveido Tkinter logu
csv_data_window = Tk()
csv_data_window.title("Dzīvo cenu diagramma")

# Iestata diagrammas stilu
plt.style.use('dark_background')

# Izveido diagrammu ar ass izmēriem
fig, ax = plt.subplots(figsize=(8, 3.8))

# Izveido līnijas diagrammai ar sākotnējiem tukšiem datiem
line, = ax.plot([], [], 'wo-', markersize=1, alpha=0.7)
ema_short_line, = ax.plot([], [], 'c-', label='EMA 5')  # Izmainīts uz ciklānu
ema_medium_line, = ax.plot([], [], 'y-', label='EMA 10')  # Izmainīts uz dzeltenu labākai atšķiršanai
ema_long_line, = ax.plot([], [], 'b-', label='EMA 20')

# Iestata diagrammas ass un nosaukumus
ax.set_xlim(0, 10)
ax.set_ylim(0, 2500)
ax.set_xlabel('Laiks')
ax.set_ylabel('Cena')
ax.set_title('Dzīvo cenu diagramma')
ax.legend()

# Pievieno diagrammu Tkinter logam
canvas = FigureCanvasTkAgg(fig, master=csv_data_window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, csv_data_window)
toolbar.update()
canvas.get_tk_widget().pack()

# Funkcija, lai saglabātu cenu CSV failā
def save_price_to_csv(price):
    current_time = datetime.now()
    new_data = {
        'Date': current_time,
        'Price': price
    }
    df.loc[len(df)] = new_data
    df.to_csv('gold_price.csv', index=False)

# Funkcija, lai iegūtu cenu
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
            print("Cena:", price)
            save_price_to_csv(price)
            update_chart(price)
            time.sleep(1)
    except Exception as e:
        print("Radās kļūda, iegūstot cenu:", e)
    finally:
        driver.quit()

# Funkcija, lai atjauninātu diagrammu
def update_chart(price):
    global df
    df['Date'] = pd.to_datetime(df['Date'])
    
    if len(df) > 60:
        plot_data = df.iloc[-60:]
    else:
        plot_data = df
    
    # Atjaunina cenu līniju ar nosacītu krāsošanu
    for i in range(1, len(plot_data)):
        color = 'g' if plot_data['Price'].iloc[i] > plot_data['Price'].iloc[i - 1] else 'r'
        ax.plot(plot_data['Date'].iloc[i-1:i+1], plot_data['Price'].iloc[i-1:i+1], color, linewidth=2)  # Biezākas līnijas
    
    if len(df) > 1:
        plot_data.loc[:, 'EMA 5'] = plot_data['Price'].ewm(span=5, adjust=False).mean()
        plot_data.loc[:, 'EMA 10'] = plot_data['Price'].ewm(span=10, adjust=False).mean()
        plot_data.loc[:, 'EMA 20'] = plot_data['Price'].ewm(span=20, adjust=False).mean()
        
        ema_short_line.set_data(plot_data['Date'], plot_data['EMA 5'])
        ema_medium_line.set_data(plot_data['Date'], plot_data['EMA 10'])
        ema_long_line.set_data(plot_data['Date'], plot_data['EMA 20'])

        # Atjauno EMA līnijas diagrammā
        ax.plot(plot_data['Date'], plot_data['EMA 5'], 'c-', label='EMA 5')  # Ciklāns EMA 5
        ax.plot(plot_data['Date'], plot_data['EMA 10'], 'y-', label='EMA 10')  # Dzeltena EMA 10
        ax.plot(plot_data['Date'], plot_data['EMA 20'], 'b-', label='EMA 20')

        # Pārbauda īsā tirdzniecības signālu
        check_short_trade(plot_data)

    ax.relim()
    ax.autoscale_view()
    
    if len(df) > 1:
        ax.set_xlim(plot_data['Date'].iloc[0], plot_data['Date'].iloc[-1])
    elif len(df) == 1:
        single_point = plot_data['Date'].iloc[0]
        ax.set_xlim(single_point - pd.Timedelta(seconds=1), single_point + pd.Timedelta(seconds=1))
    
    # Dinamiska y-ass ierobežojumu iestatīšana
    ymin = min(price - 0.2, plot_data['Price'].min() - 0.2)
    ymax = max(price + 0.2, plot_data['Price'].max() + 0.2)
    ax.set_ylim(ymin, ymax)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
    fig.autofmt_xdate()
    
    canvas.draw()

# Funkcija, lai pārbaudītu īsā tirdzniecības signālus
def check_short_trade(plot_data):
    if len(plot_data) < 20:  # Nodrošina pietiekami daudz datus EMA aprēķināšanai
        return

    ema_5 = plot_data['EMA 5'].iloc[-1]
    ema_10 = plot_data['EMA 10'].iloc[-1]
    ema_20 = plot_data['EMA 20'].iloc[-1]
    price = plot_data['Price'].iloc[-1]

    # Īsā tirdzniecības nosacījums
    if ema_5 < ema_10 < ema_20 and price < ema_5:
        print("Īsā tirdzniecības signāls pie:", plot_data['Date'].iloc[-1])

# Sāk cenu datu iegūšanu atsevišķā pavedienā
threading.Thread(target=fetch_price, daemon=True).start()
csv_data_window.mainloop()
