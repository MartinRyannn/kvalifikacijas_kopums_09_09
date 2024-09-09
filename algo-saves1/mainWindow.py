from tkinter import *
import customtkinter
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import threading
import matplotlib.dates as mdates

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


mainWindow = customtkinter.CTk(fg_color="#111111")
width = mainWindow.winfo_screenwidth()
height = mainWindow.winfo_screenheight()
mainWindow.geometry("%dx%d+0+0" % (width - 10, height))
mainWindow.title("GOLDOMATIC TRADER")

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


my_image = customtkinter.CTkImage(light_image=Image.open('images/goldLogo.png'),
                                  dark_image=Image.open('images/goldLogo.png'),
                                  size=(350, 50))
my_label = customtkinter.CTkLabel(mainWindow, text="", image=my_image)
my_label.pack(pady=0)

frame_width = int(0.45 * width)
frame_height = int(0.83 * height)
frame_width2 = int(0.50 * width)
screener_width = int(0.35 * width)
screener_height = int(0.30 * height)

flag_frame_x = width - 320
flag_frame_y = 20


leftFrame = customtkinter.CTkFrame(master=mainWindow, width=frame_width, height=frame_height, fg_color="#DC2C2C")
leftFrame.pack()
leftFrame.place(x=20, y=70)

rightFrame = customtkinter.CTkFrame(master=mainWindow, width=frame_width2, height=frame_height, fg_color="#000000")
rightFrame.pack()
rightFrame.place(x=width - frame_width2 - 20, y=60)

priceFrame = customtkinter.CTkFrame(master=mainWindow, width=200, height=40, fg_color="#181818")
priceFrame.pack()
priceFrame.place(x=260, y=80)

priceLabel = customtkinter.CTkLabel(master=priceFrame, text="", text_color="white", font=("Arial", 23))
priceLabel.place(relx=0.5, rely=0.5, anchor='center')

screenerFrame1 = customtkinter.CTkFrame(master=leftFrame, width=screener_width, height=screener_height, fg_color="#FFFFFF")
screenerFrame1.pack()
screenerFrame1.place(x=30, y=60)

screenerFrame2 = customtkinter.CTkFrame(master=leftFrame, width=screener_width, height=screener_height, fg_color="#4400FF")
screenerFrame2.pack()
screenerFrame2.place(x=30, y=490)

flagFrame = customtkinter.CTkFrame(master=mainWindow, width=300, height=110, fg_color="#A9A9A9")
flagFrame.pack()
flagFrame.place(x=flag_frame_x, y=flag_frame_y)

df = pd.DataFrame(columns=["Date", "Price"])

plt.style.use('dark_background')


fig, ax = plt.subplots(figsize=(8, 3.8))

line, = ax.plot([], [], 'wo-', markersize=1, alpha=0.7)
ema_short_line, = ax.plot([], [], 'c-', label='EMA 5')
ema_medium_line, = ax.plot([], [], 'y-', label='EMA 10')
ema_long_line, = ax.plot([], [], 'b-', label='EMA 20')

ax.set_xlim(0, 10)
ax.set_ylim(0, 2500)
ax.set_xlabel('Time')
ax.set_ylabel('Price')
ax.set_title('Live Price Chart')
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=screenerFrame1)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, screenerFrame1)
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


def update_chart(price):
    global df
    df['Date'] = pd.to_datetime(df['Date'])
    
    if len(df) > 30:
        plot_data = df.iloc[-30:]
    else:
        plot_data = df
    
    ax.cla()

    for i in range(1, len(plot_data)):
        color = 'g' if plot_data['Price'].iloc[i] > plot_data['Price'].iloc[i - 1] else 'r'
        ax.plot(plot_data['Date'].iloc[i-1:i+1], plot_data['Price'].iloc[i-1:i+1], color, linewidth=2)

    if len(df) > 1:
        plot_data.loc[:, 'EMA 5'] = plot_data['Price'].ewm(span=5, adjust=False).mean()
        plot_data.loc[:, 'EMA 10'] = plot_data['Price'].ewm(span=10, adjust=False).mean()
        plot_data.loc[:, 'EMA 20'] = plot_data['Price'].ewm(span=20, adjust=False).mean()

        
        ema_short_line.set_data(plot_data['Date'], plot_data['EMA 5'])
        ema_medium_line.set_data(plot_data['Date'], plot_data['EMA 10'])
        ema_long_line.set_data(plot_data['Date'], plot_data['EMA 20'])

        ax.plot(plot_data['Date'], plot_data['EMA 5'], 'c-', label='EMA 5')
        ax.plot(plot_data['Date'], plot_data['EMA 10'], 'y-', label='EMA 10')
        ax.plot(plot_data['Date'], plot_data['EMA 20'], 'b-', label='EMA 20')

        check_short_trade(plot_data)

    ax.relim()
    ax.autoscale_view()
    
    if len(df) > 1:
        ax.set_xlim(plot_data['Date'].iloc[0], plot_data['Date'].iloc[-1])
    elif len(df) == 1:
        single_point = plot_data['Date'].iloc[0]
        ax.set_xlim(single_point - pd.Timedelta(seconds=1), single_point + pd.Timedelta(seconds=1))
    
    ymin = min(price - 0.2, plot_data['Price'].min() - 0.2)
    ymax = max(price + 0.2, plot_data['Price'].max() + 0.2)
    ax.set_ylim(ymin, ymax)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Live Price Chart')
    ax.legend()
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
    fig.autofmt_xdate()
    
    priceLabel.configure(text=f"{price:.2f}")
    
    canvas.draw()


def check_short_trade(plot_data):
    if len(plot_data) < 20: 
        return

    ema_5 = plot_data['EMA 5'].iloc[-1]
    ema_10 = plot_data['EMA 10'].iloc[-1]
    ema_20 = plot_data['EMA 20'].iloc[-1]
    price = plot_data['Price'].iloc[-1]

    if ema_5 < ema_10 < ema_20 and price < ema_5:
        print("Short Trade Signal at:", plot_data['Date'].iloc[-1])

threading.Thread(target=fetch_price, daemon=True).start()

mainWindow.mainloop()
