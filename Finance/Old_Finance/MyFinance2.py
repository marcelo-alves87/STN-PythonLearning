import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import mpl_finance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import pdb

style.use('ggplot')

def ohlcVolume(x):
    
    if len(x):
        ohlc={ "open":x["Open"][0],"high":max(x["High"]),"low":min(x["Low"]),"close":x["Adj Close"][-1],"volume":sum(x["Volume"])}
        return pd.Series(ohlc)

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
   
ticker = 'HAPV3'
database = 'Testes/2021-12-30/stock_dfs/'
#df = pd.read_csv('natura.csv', parse_dates=True, index_col=0)
df = pd.read_csv(database + ticker + '.csv', parse_dates=True, index_col=0)
df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()


#df_ohlc = df['Adj Close'].resample('B').ohlc()

df_ohlc=df.resample('B').apply(ohlcVolume)
#df_volume = df['Volume'].resample('W-MON').sum()
pdb.set_trace()
df_ohlc.reset_index(inplace=True)
df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)

ax1.xaxis_date()

candlestick_ohlc(ax1, df_ohlc.values, colorup='g')
ax1.plot(df.index, df['SMA'], label ='SMA', color = 'red')
ax1.plot(df.index, df['EMA'], label='EMA', color = 'green')
#ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
RSI(df, ax2)
plt.title(ticker)
plt.show()


