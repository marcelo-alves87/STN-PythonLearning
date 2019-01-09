import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd

style.use('ggplot')

with open("ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)
    
data = []    
for ticker in tickers:
    df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
    df.set_index('Date', inplace=True)
    df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
    df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
    data.append([ticker, df['EMA'][-1] - df['SMA'][-1]])
    
data = sorted(data,key=lambda x: x[1])
for row in data:
    plt.scatter(row[0], row[1])
plt.show()
    
