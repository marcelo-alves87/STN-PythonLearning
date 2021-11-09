import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np

style.use('ggplot')

def create_dict():
    with open("ibovespatickers.pickle", "rb") as f:
        tickers = pickle.load(f)
        
    data = {}    
    for ticker in tickers:
        try:        
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            adj_close = df['Adj Close'][-1]
            open1 = df['Open'][-1]
            data.update({ticker : (adj_close/open1) - 1 })
        except:
            pass
    return data

def plot(ticker1, ticker2):

    
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
    ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
    ax1.xaxis_date()

    df = pd.read_csv('stock_dfs/' + ticker1 + '.csv', parse_dates=True, index_col=0)
    df1 = df['Adj Close']
    df1.plot(ax=ax1,label=ticker1) 
    list1 = df['Adj Close'].tolist()    

    df = pd.read_csv('stock_dfs/' + ticker2 + '.csv', parse_dates=True, index_col=0)
    df2 = df['Adj Close']
    df2.plot(ax=ax1,label=ticker2)
    list2 = df['Adj Close'].tolist()
    
    
    if df1.max() > df2.max():
        df1 = df1.divide(df2)        
        df1 = df1.subtract(1)
        df1.plot(ax=ax2, c='purple')
    else:
        df2 = df2.divide(df1)
        df2 = df2.subtract(1)
        roll = df2.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax2, c='lightcoral')
        print('roll',roll['2021-09-15'])
        print(df2['2021-09-15'])
        df2.plot(ax=ax2, c='brown')
    
    ax1.fill_between(df.index.values, list1, list2, color="grey", alpha="0.3")    
    ax1.legend()
    #plt.show()
    
dict1 = create_dict()
#print(data['LWSA3'])

##df = pd.read_csv('ibovespa_joined_closes.csv')
##df_corr = df.corr()
##for index, data in df_corr.iteritems():
##    for index1, data1 in data.iteritems():
##        if data1 >= 0.98 and index != index1:
##            print(('{} e {}  fator de correlação: {}').format(index, index1, data1))
##            
plot('AMAR3', 'MTRE3')
