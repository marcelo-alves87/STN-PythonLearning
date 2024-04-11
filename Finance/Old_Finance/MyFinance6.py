import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
import pdb
import os
import datetime as dt

style.use('ggplot')

dict = {}

def get_details(ticker):
    df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
    if 'Datetime' in df.columns:
        df['Datetime'] = df['Datetime'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))
        df = df[df['Datetime'].dt.date ==  df['Datetime'].iloc[-1].date()]
        return [df['Close'].iloc[0],df['Volume'].sum()]
    elif 'Date' in df.columns:
        return [df['Close'][0],int(df['Volume'].mean())]
    else:
        return 0
    
def check_volume(tickers):
    for ticker in tickers:
        if ticker in dict:
            vol = dict[ticker]
        else:            
            vol = get_volume(ticker)
            dict[ticker] = vol
        if vol < 10**6:
            return False
    return True

def list_tickets(volume):
    tickers = []
    results = []
    for file_path in os.listdir('stock_dfs'):
        tickers.append(file_path.replace('.csv',''))
    for ticker in tickers:
        details = get_details(ticker)
        results.append([ticker, details[0], details[1]])  
    df = pd.DataFrame(results)
    df = df.sort_values([1,2])
    for i,v in df.iterrows():
        if v[2] > volume:                   
            print('{} -> Last: {} Volume: {} M'.format(v[0], round(v[1],2), round(v[2]/volume,3)))

def visualize_data2():
    df = pd.read_csv('ibovespa_joined_closes.csv')
    df_corr = df.corr()
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
            if data1 >= 0.97 and index != index1 and check_volume([index,index1]):                
                print(('{} e {} fator de correlação: {}').format(index, index1, data1))
    

#visualize_data2()
list_tickets(10**6)                

