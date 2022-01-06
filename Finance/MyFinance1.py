import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')

##start = dt.datetime(2015, 1, 1)
##end = dt.datetime.now()
##df = web.DataReader("NATU3.SA", 'yahoo')
##
##df.to_csv('natura.csv')

##df = pd.read_csv('natura.csv', parse_dates=True, index_col=0)
##df['Adj Close'].plot()
##plt.show()


def RSI(df, axis, window_length = 14):

    #df = pd.read_csv(database + '/' + ticker + '.csv', parse_dates=True, index_col=0)
    # Get just the adjusted close
    # Get the difference in price from previous step
    delta = df['Adj Close'].diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    #delta = delta[1:]
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
   # plt.figure(figsize=(8, 6))
##    rsi_ewma.plot()
##    rsi_sma.plot()
    axis.plot(df.index,rsi_rma)
    axis.axhline(y=70, color='b', linestyle='--')
    axis.axhline(y=50, color='black', linestyle='--')
    axis.axhline(y=30, color='b', linestyle='--')
    #plt.legend(['RSI via EWMA', 'RSI via SMA', 'RSI via RMA/SMMA/MMA (TradingView)'])
    #plt.show()
   

  
#plt.show()

ticker = 'BRCO11'
database = 'Testes/2021-12-30/stock_dfs/'

#RSI(ticker, database)  

df = pd.read_csv(database + ticker + '.csv', parse_dates=True,index_col=0)
df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()

ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)

ax1.plot(df.index, df['Adj Close'], label='Price')
ax1.plot(df.index, df['SMA'], label ='SMA', color = 'red')
ax1.plot(df.index, df['EMA'], label='EMA', color = 'green')
x_labels = df.index.strftime('%b')
ax1.set_xticklabels(x_labels)

#ax2.bar(df.index, df['Volume'])

RSI(df, ax2)
plt.title(ticker)
ax1.legend()
plt.show()


