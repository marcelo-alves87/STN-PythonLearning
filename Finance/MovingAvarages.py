import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np

style.use('ggplot')

def plot_range(volume_min, volume_max, plot_type):
    with open("ibovespatickers.pickle", "rb") as f:
        tickers = pickle.load(f)
        
    data = []
    monotonic_factor = -3 # dois dias anteriores
    for ticker in tickers:
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-1]
            df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
            df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
            diff = df['EMA'][-1] - df['SMA'][-1]

            if last_volume >= volume_min and last_volume < volume_max:

##               if plot_type == 0: 
##                   data.append([ticker, diff])
               if plot_type == 1 and diff <= 0 and df['EMA'][monotonic_factor:].is_monotonic:
                   data.append([ticker, diff])

               elif plot_type == 2 and diff >= 0 and df['SMA'][monotonic_factor:].is_monotonic_decreasing:    
                   data.append([ticker, diff])    

               elif plot_type == 3 and df['EMA'][monotonic_factor:].is_monotonic and df['SMA'][monotonic_factor:].is_monotonic_decreasing:    
                   data.append([ticker, diff])
               
        except:
            pass
        
        

    data = sorted(data,key=lambda x: x[1])

    for row in data:
        plt.scatter(row[0], row[1])

    if len(data) > 0:
        y_min = min(data, key = lambda t: t[1])
        y_max = max(data, key = lambda t: t[1])

        plt.yticks(np.arange(y_min[1], y_max[1], step=0.1))

plt.figure()

plt.subplot(221)
plt.title('EMA')
plot_range(10**6,10**8,1)

plt.subplot(222)
plt.title('SMA')
plot_range(10**6,10**8,2)

plt.subplot(212)
plt.title('MA Cross')
plot_range(10**6,10**8,3)


plt.show()
    
