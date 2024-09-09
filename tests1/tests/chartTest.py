import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'None'

df = pd.read_csv("XAUUSD15.CSV", delimiter='\t', header=None)
df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M')
df.set_index('Date', inplace=True)

style = "nightclouds"
last_candles = df.iloc[-80:]

mpf.plot(last_candles, type='candle', style=style, 
         volume=False, 
         figscale=0.5, ylabel='', tight_layout=True, figratio=(6, 3),
         xrotation=0, datetime_format='%Y-%m-%d %H:%M')


mpf.show()
