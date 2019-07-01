import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np

style.use('ggplot')

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
        if last_volume >= 10**6.5 and last_volume < 10**7:
           data.append([ticker, diff])
    except:
        pass
    
    

data = sorted(data,key=lambda x: x[1])

for row in data:
    plt.scatter(row[0], row[1])
y_min = min(data, key = lambda t: t[1])
y_max = max(data, key = lambda t: t[1])

plt.yticks(np.arange(y_min[1], y_max[1], step=0.1))    
plt.show()
    
