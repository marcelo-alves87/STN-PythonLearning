import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np
import pdb
import math

style.use('ggplot')

def sort_(e):    
    i = float(e[1])
    if math.isnan(i):
        i = 0
    return i


with open("ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)
    
data = []    
for ticker in tickers:
    try:
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        last_volume = df['Volume'][-2]
        df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
        df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
        diff = df['EMA'][-1] - df['SMA'][-1]
        if last_volume > 10**6 and last_volume < 10**7:           
           diff = abs((df['EMA'][-1] - df['Adj Close'][-1])/df['Adj Close'][-1])
           if df['EMA'][-1] > df['SMA'][-1] and df['Adj Close'][-1] < df['EMA'][-1]:
               data.append([ticker, diff])
    except:
        pass
    
    

#data = sorted(data,reverse=True, key=lambda x: x[1])
data.sort(reverse=True, key=sort_)
print(data)
##for row in data:
##    #plt.scatter(row[0], row[1])
##    print(row)

#plt.show()
