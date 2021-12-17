import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np
import pdb
import math

style.use('ggplot')

def RSI(ticker, window_length = 14):

    df = pd.read_csv('stock_dfs' + '/' + ticker + '.csv', parse_dates=True, index_col=0)
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


    # Compare graphically
    plt.figure(figsize=(8, 6))
##    rsi_ewma.plot()
##    rsi_sma.plot()
    rsi_rma.plot()
    plt.axhline(y=70, color='b', linestyle='--')
    plt.axhline(y=50, color='black', linestyle='--')
    plt.axhline(y=30, color='b', linestyle='--')
    #plt.legend(['RSI via EWMA', 'RSI via SMA', 'RSI via RMA/SMMA/MMA (TradingView)'])
    plt.show()
   

RSI('VIVT3')    
#plt.show()
