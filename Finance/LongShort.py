###
## 1. Se a linha roxa estiver acima da linha lightcoral , vende-se a ação vermelha pois ela vai cair e compra a linha azul que vai subir
## 2. Se a linha roxa estiver abaixo da linha lightcoral, vende-se a ação azul pois ela vai cair e compra a linha vermelha que vai subir


import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime as dt
import pdb

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

def print_corr():
    dict1 = create_dict()
    print(data['LWSA3'])

    df = pd.read_csv('ibovespa_joined_closes.csv')
    df_corr = df.corr()
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
            if data1 >= 0.98 and index != index1:
                print(('{} e {}  fator de correlação: {}').format(index, index1, data1))
                



def plot(ticker1, ticker2):

    
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=2, colspan=1)
    ax2 = plt.subplot2grid((6,1), (2,0), rowspan=2, colspan=1)
    ax3 = plt.subplot2grid((6,1), (4,0), rowspan=1, colspan=1)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    ax1.get_shared_x_axes().join(ax1, ax3)
    ax1.get_shared_x_axes().join(ax2, ax3)
    ax1.get_shared_x_axes().join(ax1, ax2)
    
    df = pd.read_csv('stock_dfs/' + ticker1 + '.csv', parse_dates=True, index_col=0)
    df1 = df['Adj Close']
    df1.plot(ax=ax1,label=ticker1, c='red') 
    list1 = df['Adj Close'].tolist()    

    df = pd.read_csv('stock_dfs/' + ticker2 + '.csv', parse_dates=True, index_col=0)
    df2 = df['Adj Close']
    df2.plot(ax=ax2,label=ticker2, c='blue')
    list2 = df['Adj Close'].tolist()
    
    
    if df1.max() > df2.max():
        df1 = df1.divide(df2)        
        df1 = df1.subtract(1)
        roll = df1.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax3, c='lightcoral')        
        df1.plot(ax=ax3, c='purple')
    else:
        df2 = df2.divide(df1)
        df2 = df2.subtract(1)
        roll = df2.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax3, c='lightcoral')        
        df2.plot(ax=ax3, c='brown')
    
    #ax1.fill_between(df.index.values, list1, list2, color="grey", alpha="0.3")    
    ax1.legend()
    plt.show()

def sort_(e):
    return e['diff']

def sort2_(e):
    return e['corr']

def mean_diff(date):
    
    date_str = date.strftime('%Y-%m-%d')
    yesterday = date - dt.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    df = pd.read_csv('ibovespa_joined_closes.csv')
    df_corr = df.corr()
    tickets = []
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
           if data1 >= 0.9 and index != index1:
               try:                   
                   df1 = pd.read_csv('stock_dfs/' + index + '.csv', parse_dates=True, index_col=0)
                   df1 = df1['Adj Close']

                   df11 = pd.read_csv('stock_dfs/' + index + '.csv', parse_dates=True, index_col=0)
                   df11 = df11['Volume']
                   df11_value = round(df11[yesterday_str] / 10**6,3)
                  
                   df2 = pd.read_csv('stock_dfs/' + index1 + '.csv', parse_dates=True, index_col=0)
                   df2 = df2['Adj Close']

                   df22 = pd.read_csv('stock_dfs/' + index1 + '.csv', parse_dates=True, index_col=0)
                   df22 = df22['Volume'] 
                   df22_value = round(df22[yesterday_str] / 10**6,3)
                   
                   value1 = df1[yesterday_str]
                   value2 = df2[yesterday_str]
                   
                   if value1 > value2 and df11_value > 1 and df22_value > 1:
                       df1 = df1.divide(df2)
                       df1 = df1.subtract(1)
                       value1 = df1[date_str]
                       mean10 = df1.rolling(window=10, min_periods=0).mean()
                       mean10_value = mean10[date_str]
                       diff = round(abs(value1 - mean10_value),3)
                       
                       tickets.append({'date' : date_str, 'ticket1' :index, 'ticket2' :index1, 'corr' : round(data1,3), 'diff' : diff, 'vol1' : df11_value , 'vol2' : df22_value})                                          
               except:
                   pass
               
    return tickets

tickets = mean_diff(dt.date.today())
tickets.sort(reverse=True, key=sort_)
for ticket in tickets:
    if ticket['diff'] > 0:
       print(('Data: {} : {} e {} = volume ({} milhões e {} milhões);  Fator de correlação: {}, Diferença com média: {}').format(ticket['date'],ticket['ticket1'], ticket['ticket2'], ticket['vol1'], ticket['vol2'], ticket['corr'], ticket['diff']))
    
#plot('ALPA4','GFSA3')

            
