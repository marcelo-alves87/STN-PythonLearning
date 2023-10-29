import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np
import pdb
import math
import pdb

style.use('ggplot')

def sort_(e):    
    i = float(e[3])
    if math.isnan(i):
        i = 0
    return i

def biggest_highs(tickers):
    data = []    
    for ticker in tickers:
        try:            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-2]
            
            if last_volume > 10**6 and last_volume < 10**9:           
                data.append([ticker, 1 - df['Open'][-1]/df['Adj Close'][-1]])
        except:
            pass
    return data

def ret_bullish_bearish_avarages(tickers):
    data = []    
    for ticker in tickers:
        try:            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-2]
            df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
            df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
            if last_volume > 10**6 and last_volume < 10**9:           
               diff = 1 - df['EMA'][-1]/df['Adj Close'][-1]
               diff2 = 1 - df['SMA'][-1]/df['Adj Close'].max()
               data.append([ticker, diff, diff2, diff/diff2])
        except:
            pass
    return data


def ret_bullish_avarages(tickers):
    data = []    
    for ticker in tickers:
        try:            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-2]
            df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
            if last_volume > 10**6 and last_volume < 10**9:           
               diff = 1 - df['EMA'][-1]/df['Adj Close'][-1]
               data.append([ticker, diff])
        except:
            pass
    return data

def ret_bearish_avarages(tickers):
    data = []    
    for ticker in tickers:
        try:            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-2]
            df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
            if last_volume > 10**6 and last_volume < 10**9:           
               diff = 1 - df['SMA'][-1]/df['Adj Close'].max()
               data.append([ticker, diff])
        except:
            pass
    return data


def ret_data_moving_avarages_(tickers):
    data = []    
    for ticker in tickers:
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-2]
            df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
            df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
            diff = (df['EMA'][-1] - df['SMA'][-1])/df['EMA'][-1]            
            if last_volume > 10**6 and last_volume < 10**7:
               data.append([ticker, diff])
        except:
            pass
    return data    

def ret_data_moving_avarages(tickers):
    data = []    
    for ticker in tickers:
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Datetime', inplace=True)
            df = df[df.index > '2023-10-27']
            volume = (df['Volume'] * df['Adj Close']).sum()
            if volume > 10 ** 8:
                data.append([ticker, volume])
        except:
            pass
    return data

with open("ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)        


data = ret_data_moving_avarages(tickers)
#data = ret_bearish_avarages(tickers)
#data = ret_bullish_avarages(tickers)
#data = ret_data_moving_avarages_(tickers)
#data = biggest_highs(tickers)
#data = sorted(data, key=lambda x: x[1])
#data = ret_bullish_bearish_avarages(tickers)
#data.sort(key=sort_)
#print(data)
#for row in data:
#    plt.scatter(row[0], row[1])
#    print(row)

#plt.show()
print(len(data))
for i in data:
    print("{} has volume: {}".format(i[0], i[1]))
