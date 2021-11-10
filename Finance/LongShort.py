import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import numpy as np
import datetime

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
        roll = df1.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax2, c='lightcoral')        
        df1.plot(ax=ax2, c='purple')
    else:
        df2 = df2.divide(df1)
        df2 = df2.subtract(1)
        roll = df2.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax2, c='lightcoral')        
        df2.plot(ax=ax2, c='brown')
    
    #ax1.fill_between(df.index.values, list1, list2, color="grey", alpha="0.3")    
    ax1.legend()
    plt.show()

def sort_(e):
    return e['diff']

def sort2_(e):
    return e['corr']

def mean_diff(date):    
    date_str = date.strftime('%Y-%m-%d')
    df = pd.read_csv('ibovespa_joined_closes.csv')
    df_corr = df.corr()
    tickets = []
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
           if data1 >= 0.96 and index != index1:
               try: 
                   df1 = pd.read_csv('stock_dfs/' + index + '.csv', parse_dates=True, index_col=0)
                   df1 = df1['Adj Close']
                   df2 = pd.read_csv('stock_dfs/' + index1 + '.csv', parse_dates=True, index_col=0)
                   df2 = df2['Adj Close']
                   value1 = df1[date_str]
                   value2 = df2[date_str]                   
                   if value1 > value2:
                       df1 = df1.divide(df2)
                       df1 = df1.subtract(1)
                       value1 = df1[date_str]
                       mean10 = df1.rolling(window=10, min_periods=0).mean()
                       mean10_value = mean10[date_str]
                       tickets.append({'date' : date_str, 'ticket1' :index, 'ticket2' :index1, 'corr' :data1, 'diff' : value1 - mean10_value})                                          
               except:
                   pass
               
    return tickets

tickets = mean_diff(datetime.datetime(2021, 11, 9))
tickets.sort(reverse=True, key=sort_)
#tickets = tickets[:100]
#tickets.sort(reverse=True, key=sort2_)
for ticket in tickets:
    print(('Data: {} : {} e {};  Fator de correlação: {}, Diferença com média: {}').format(ticket['date'],ticket['ticket1'], ticket['ticket2'], ticket['corr'], ticket['diff']))
 
#plot('LREN3','AMAR3')

            
