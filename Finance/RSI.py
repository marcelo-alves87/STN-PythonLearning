import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np
import pdb
import math
import datetime as dt

style.use('ggplot')

def plot(rsi_rma):
    # Compare graphically
    plt.figure(figsize=(8, 6))
    ##    rsi_ewma.plot()
    ##    rsi_sma.plot()
    rsi_rma.plot()
    #print(rsi_rma[-1])
    plt.axhline(y=70, color='b', linestyle='--')
    plt.axhline(y=50, color='black', linestyle='--')
    plt.axhline(y=30, color='b', linestyle='--')
    #plt.legend(['RSI via EWMA', 'RSI via SMA', 'RSI via RMA/SMMA/MMA (TradingView)'])
    plt.show()

def show_bearish_moving(tickers):
    for i in range(30):
        for count, ticker in enumerate(tickers):
            ret = RSI(ticker, interval=i)
            if ret is not None:
                rsi, last_volume, date_str, diff, last_sma = ret
                try:
                    if rsi[-1] >= 70 and last_sma > diff and last_volume > 10**6 and last_volume < 10**9:
                        print('Date: {}, Ticker: {} '.format(date_str,ticker))
                except:
                    pass

def RSI(ticker, window_length = 14, interval = 0):
    try:        
        date = dt.date.today() - dt.timedelta(days=interval)        
        df = pd.read_csv('stock_dfs' + '/' + ticker + '.csv', parse_dates=True, index_col=0)
        df = df[:date]
        df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
        date_str = date.strftime('%Y-%m-%d')
        last_volume = df['Volume'][date_str]
        last_sma = df['SMA'][date_str]

        df_max = df['Adj Close'].max()
        df_min = df['Adj Close'].min()
        
        diff = (df_max - df_min)/4
        diff = 2*diff + df_min #media vermelha acima de 2 quartos       
        
        # Get just the adjusted close
        # Get the difference in price from previous step
        delta = df['Adj Close'].diff()
        # Get rid of the first row, which is NaN since it did not have a previous 
        # row to calculate the differences
        delta = delta[1:]
        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
        # Calculate the RSI based on EWMA
        # Reminder: Try to provide at least `window_length * 4` data points!
    ##    roll_up = up.ewm(span=window_length).mean()
    ##    roll_down = down.ewm(span=window_length).mean()
    ##    rs = roll_up / roll_down
    ##    rsi_ewma = 100.0 - (100.0 / (1.0 + rs))

        # Calculate the RSI based on SMA
    ##    roll_up = up.rolling(window_length).mean()
    ##    roll_down = down.rolling(window_length).mean()
    ##    rs = roll_up / roll_down
    ##    rsi_sma = 100.0 - (100.0 / (1.0 + rs))

        # Calculate the RSI based on RMA/SMMA/MMA
        # Reminder: Try to provide at least `window_length * 4` data points!
        # Note: This should most closely match TradingView.
        alpha = 1 / window_length
        roll_up = up.ewm(alpha=alpha).mean()
        roll_down = down.ewm(alpha=alpha).mean()
        rs = roll_up / roll_down
        rsi_rma = 100.0 - (100.0 / (1.0 + rs))
        return rsi_rma, last_volume, date_str, diff, last_sma
    except:
        return None

def RSI_calc(df,  window_length = 14):
    # Get just the adjusted close
    # Get the difference in price from previous step
    delta = df['Adj Close'].diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    delta = delta[1:]
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
    # Calculate the RSI based on EWMA
    # Reminder: Try to provide at least `window_length * 4` data points!
##    roll_up = up.ewm(span=window_length).mean()
##    roll_down = down.ewm(span=window_length).mean()
##    rs = roll_up / roll_down
##    rsi_ewma = 100.0 - (100.0 / (1.0 + rs))

    # Calculate the RSI based on SMA
##    roll_up = up.rolling(window_length).mean()
##    roll_down = down.rolling(window_length).mean()
##    rs = roll_up / roll_down
##    rsi_sma = 100.0 - (100.0 / (1.0 + rs))

    # Calculate the RSI based on RMA/SMMA/MMA
    # Reminder: Try to provide at least `window_length * 4` data points!
    # Note: This should most closely match TradingView.
    alpha = 1 / window_length
    roll_up = up.ewm(alpha=alpha).mean()
    roll_down = down.ewm(alpha=alpha).mean()
    rs = roll_up / roll_down
    rsi_rma = 100.0 - (100.0 / (1.0 + rs))

    return rsi_rma

def RSI_diff(ticker, window_length = 14, interval = 1):
    try:
        
        date_now = dt.date.today()    
        date_old = date_now - dt.timedelta(days=interval)        

        df = pd.read_csv('stock_dfs' + '/' + ticker + '.csv', parse_dates=True, index_col=0)
        df_old = df[:date_old]        
        
        date_old_str = date_old.strftime('%Y-%m-%d')
        last_volume = df['Volume'][-2]

        df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
        df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
            
        old_rsi = RSI_calc(df_old)[-1]
        rsi = RSI_calc(df)[-1]
        old_price = df_old['Adj Close'][-1]
        old_open = df_old['Open'][-1]
        old_low = df_old['Low'][-1]
        high = df['High'][-1]
        sma = df['SMA'][-1]
        ema = df['EMA'][-1]
        return rsi, old_rsi, last_volume, date_old_str, old_price, old_open, old_low, high, sma, ema
    except:
        return None



with open("ibovespatickers.pickle", "rb") as f:
        tickers = pickle.load(f)
show_bearish_moving(tickers)
##hold = []
##for i in range(1,30):    
##        for count, ticker in enumerate(tickers):
##            ret = RSI_diff(ticker, interval=i)            
##            if ret is not None:
##                rsi, old_rsi, last_volume, date_old_str, old_price, old_open, old_low, high, sma, ema = ret
##                try:
##                    if rsi < old_rsi and high > old_open and ticker not in hold and ema > sma and last_volume > 10**6:
##                        print('Date: {}, Ticker: {}'.format(date_old_str,ticker))
##                        hold.append(ticker)                        
##                except:
##                    pass
