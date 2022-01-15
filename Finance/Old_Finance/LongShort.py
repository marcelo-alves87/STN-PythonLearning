###
## 1. Se a linha roxa estiver acima da linha lightcoral , vende-se a ação vermelha pois ela vai cair e compra a linha azul que vai subir (V1)
## 2. Se a linha roxa estiver abaixo da linha lightcoral, vende-se a ação azul pois ela vai cair e compra a linha vermelha que vai subir (C1)
## 3. Se a linha verde estiver abaixo da linha laranja, vende-se a ação vermelha pois ela vai cair e compra a linha azul que vai subir (C2)
## 4. Se a linha verde estiver acima da linha laranja, vende-se a ação azul pois ela vai cair e compra a linha vermelha que vai subir (V2)

import traceback
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime as dt
import pdb
import math
import os

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
                



def plot(ticker1, ticker2, database='stock_dfs', start_date = None, end_date = None):
   
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=2, colspan=1)
    ax2 = plt.subplot2grid((6,1), (2,0), rowspan=2, colspan=1)
    ax3 = plt.subplot2grid((6,1), (4,0), rowspan=1, colspan=1)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    ax1.get_shared_x_axes().join(ax1, ax3)
    ax1.get_shared_x_axes().join(ax2, ax3)
    ax1.get_shared_x_axes().join(ax1, ax2)
    
    df = pd.read_csv(database + '/' + ticker1 + '.csv', parse_dates=True, index_col=0)
    df1 = df['Adj Close']
    if start_date is not None:
        df1 = df1[start_date:]
    if end_date is not None:
        df1 = df1[:end_date]
    df1.plot(ax=ax1,label=ticker1, c='red') 
    list1 = df['Adj Close'].tolist()    

    df = pd.read_csv(database + '/' + ticker2 + '.csv', parse_dates=True, index_col=0)
    df2 = df['Adj Close']
    if start_date is not None:
        df2 = df2[start_date:]
    if end_date is not None:
        df2 = df2[:end_date]
        
    df2.plot(ax=ax2,label=ticker2, c='blue')
    list2 = df['Adj Close'].tolist()
    
    
    if df1.max() > df2.max():
        dfs = df1.subtract(df2)        
        df1 = dfs.divide(df1)
        roll = df1.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax3, c='lightcoral')        
        df1.plot(ax=ax3, c='purple')
    else:
        dfs = df2.subtract(df1) 
        df2 = dfs.divide(df2)
        roll = df2.rolling(window=10, min_periods=0).mean()
        roll.plot(ax=ax3, c='orange')        
        df2.plot(ax=ax3, c='darkgreen')
    
    #ax1.fill_between(df.index.values, list1, list2, color="grey", alpha="0.3")    
    ax1.legend()
    ax2.legend()
    plt.show()

def sort_(e):
    i = float(e['diff'])
    if math.isnan(i):
        i = 0
    return i

def load_tickers(file="tickers.pickle"):
    with open(file, "rb") as f:
        tickers = pickle.load(f)
    return tickers

def mean_diff_value(df1,df2,date_str):
       
       dfs = df1.subtract(df2)
       df1 = dfs.divide(df1)

       if isinstance(df1[date_str],pd.Series):                                                  
           value1 = float(df1[date_str][0])
       elif isinstance(df1[date_str],np.float64):
           value1 = float(df1[date_str])
       
       
       mean10 = df1.rolling(window=10, min_periods=0).mean()

       if isinstance(mean10[date_str],pd.Series):                                                  
           mean10_value = float(mean10[date_str][0])
       elif isinstance(mean10[date_str],np.float64):
           mean10_value = float(mean10[date_str])

        
       
        
       if value1 > mean10_value:
           diff_code = 'V'
           diff = 1 - (mean10_value/value1)
       else:
           diff = 1 - (value1/mean10_value)
           diff_code = 'C'
        
       
       return diff, diff_code

def mean_diff_ticker(index, index1, date_str, yesterday_str, database, start_date = None):

    try:           
       df1 = pd.read_csv(database + '/' + index + '.csv', parse_dates=True, index_col=0)
       df1 = df1['Adj Close']

       df11 = pd.read_csv(database + '/' + index + '.csv', parse_dates=True, index_col=0)
       df11 = df11['Volume']
       
      
       df2 = pd.read_csv(database + '/' + index1 + '.csv', parse_dates=True, index_col=0)
       df2 = df2['Adj Close']

       df22 = pd.read_csv(database + '/' + index1 + '.csv', parse_dates=True, index_col=0)
       df22 = df22['Volume']


       if not start_date is None:
           df1 = df1[start_date:]
           df2 = df2[start_date:]
           df11 = df11[start_date:]
           df22 = df22[start_date:]
       
       if isinstance(df11.max(),pd.Series):                      
           df11_value = round(float(df11.max()) / 10**6,3)
           value1 = float(df1.max())
       elif isinstance(df11.max(),(np.float64, np.int64)):
           df11_value = round(float(df11.max()) / 10**6,3)
           value1 = float(df1.max())
           
       if isinstance(df22.max(),pd.Series):                       
           df22_value = round(float(df22.max()) / 10**6,3)
           value2 = float(df2.max())
       elif isinstance(df22.max(),(np.float64, np.int64)):
           df22_value = round(float(df22.max()) / 10**6,3)    
           value2 = float(df2.max())
       
       
       if value1 > value2:
           diff, diff_code = mean_diff_value(df1, df2, date_str) 
           diff_code = diff_code + '1'           
       else:
           diff, diff_code = mean_diff_value(df2, df1, date_str)               
           diff_code = diff_code + '2'       

       return diff, df11_value, df22_value, diff_code    
    except:                   
       #print(traceback.format_exc())                   
       pass


def exists(ticker, index, index1):
    return ticker['ticker1'] == index and ticker['ticker2'] == index1   


# so funciona comm a base maior que a data especificada
# detalhes de date + 1
def details(ticker, date , database='stock_dfs', verbose = False, testing = True):

    df = pd.read_csv(database + '/' + ticker + '.csv', parse_dates=True, index_col=0)
    df = df.loc[date:]
 
    today_close = df['Adj Close'][0]
    today_open = df['Open'][0]
    tomorrow_open = df['Open'][1]
    tomorrow_high = df['High'][1]
    tomorrow_low = df['Low'][1]
    tomorrow_close = df['Adj Close'][1]

    if verbose:
        print("Today Open: {}".format(today_open))
        print("Today Close: {}".format(today_close))
        print("Tomorrow Open: {}".format(tomorrow_open))
        print("Tomorrow High: {}".format(tomorrow_high))
        print("Tomorrow Low: {}".format(tomorrow_low))
        print("Tomorrow Close: {}".format(tomorrow_close))
    
    print("Variation of today open and close: {}% (today loss)".format((1 - (today_close/today_open))*100))
    print("Variation of tomorrow open and today close: {}% (opening gain)".format((1 - (today_close/tomorrow_open))*100))
    if testing:
        print("Variation of tomorrow open and close: {}% (tomorrow loss, easy level)".format((1 - (tomorrow_close/tomorrow_open))*100))
        print("Variation of tomorrow open and low: {}% (tomorrow opening loss, normal level)".format((1 - (tomorrow_low/tomorrow_open))*100))
        print("Variation of tomorrow high and close: {}% (tomorrow high loss, medium level)".format((1 - (tomorrow_close/tomorrow_high))*100))
        print("Variation of tomorrow high and low: {}% (tomorrow higher loss, high level)".format((1 - (tomorrow_low/tomorrow_high))*100))
    
    
    
                
def mean_diff(date = dt.date.today(), ticker1 = None, ticker2 = None, database = 'stock_dfs', verbose = False, corr = 0.9, start_date = None, joined_closes = 'ibovespa_joined_closes.csv', pickel_loc = "tickers.pickle"):
    
    date_str = date.strftime('%Y-%m-%d')
    yesterday = date - dt.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    df = pd.read_csv(joined_closes)    
    df_corr = df.corr()
    len1 = len(df_corr)
    if ticker1 == None or ticker2 == None:
        tickers = []
        for index, data in df_corr.iteritems():
            for index1, data1 in data.iteritems():                                
                if index != index1:
                   ret = None 
                   if corr is None:
                       ret = mean_diff_ticker(index, index1, date_str, yesterday_str, database, start_date)
                   elif data1 >= corr and data1 < (corr + 0.1):
                       ret = mean_diff_ticker(index, index1, date_str, yesterday_str, database, start_date)
                   if not ret is None:                       
                       diff, df11_value, df22_value, diff_code = ret
                       tickers.append({'date' : date_str, 'ticker1' :index, 'ticker2' :index1, 'corr' : round(data1,3), 'diff' : diff, 'vol1' : df11_value , 'vol2' : df22_value, 'diff_code' : diff_code})

                if verbose:
                    print('Doing ({}) of ({})'.format(len(tickers), len1**2))
                                       
                       
        tickers.sort(reverse=True, key=sort_)

        with open(pickel_loc,"wb") as f:
            pickle.dump(tickers,f)
    else:
        for index, data in df_corr.iteritems():
            for index1, data1 in data.iteritems():
                if index == ticker1 and index1 == ticker2:                    
                    diff, df11_value, df22_value, diff_code = mean_diff_ticker(index, index1, date_str, yesterday_str, database)
                    print(('Data: {} : {} e {} = volume ({} milhões e {} milhões);  Fator de correlação: {}, Diferença com média: {}; {}').format(date_str,index, index1, df11_value, df22_value, round(data1,3), diff, diff_code))
                    break
        
    
#mean_diff(corr=None, verbose=True)
##
#os.system('shutdown -s')

##my_ticker = 'HAPV3'
##
##          
##tickers = load_tickers(file="Testes/2021-12-02/tickers.pickle")
####
##for ticker in tickers:
##    if abs(ticker['corr']) >= 0.8 and abs(ticker['diff']) >= 1 and ticker['ticker1'] == my_ticker: 
##        print(('Data: {} : {} e {} = volume ({} milhões e {} milhões);  Fator de correlação: {}, Diferença com média: {}; {}').format(ticker['date'],ticker['ticker1'], ticker['ticker2'], ticker['vol1'], ticker['vol2'], ticker['corr'], ticker['diff'], ticker['diff_code']))
##
##
##details(my_ticker,'2021-12-02', database='Testes/2021-12-30/stock_dfs', testing=True)
##          
##dt.datetime.strptime('2021-08-16','%Y-%m-%d')      

#mean_diff(ticker1 = 'CMIN3', ticker2 =  'CURY3')
##################
######                          
#plot('AMER3', 'LEVE3')

with open("Testes/2021-12-30/ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)

ticker_pair = load_tickers(file="Testes/2021-12-02/tickers.pickle")
data = []
for ticker in tickers:
    sum = 0
    count = 0
    corr = 0
    for pair in ticker_pair:
        if abs(pair['corr']) >= 0.8 and abs(pair['diff']) >= 1 and ((pair['ticker1'] == ticker and pair['diff_code'] == 'V1') or (pair['ticker2'] == ticker and pair['diff_code'] == 'C1')):
            count += 1
            corr += abs(pair['corr'])
            sum += abs(pair['diff'])
    if count > 0:        
        data.append([ticker, count, sum, corr/count, sum*corr/count])
data = sorted(data, reverse=True, key=lambda x: x[4])

for datum in data:
    print(datum)
