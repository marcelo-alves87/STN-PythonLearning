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

#df = pd.read_csv('natura.csv', parse_dates=True, index_col=0)
#df['Adj Close'].plot()
#plt.show()

df = pd.read_csv('natura.csv', parse_dates=True,index_col=0)
df['SMA'] = df['Adj Close'].rolling(window=100, min_periods=0).mean()
df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()

ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)

ax1.plot(df.index, df['Adj Close'])
ax1.plot(df.index, df['SMA'])
ax1.plot(df.index, df['EMA'])
x_labels = df.index.strftime('%b')
ax1.set_xticklabels(x_labels)
ax2.bar(df.index, df['Volume'])
plt.show()


