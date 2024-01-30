import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
import pdb
import os
import datetime as dt

style.use('ggplot')

dict = {}

def get_volume(ticker):
    df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
    if 'Datetime' in df.columns:
        df['Datetime'] = df['Datetime'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))
        df = df[df['Datetime'].dt.date ==  df['Datetime'].iloc[-1].date()]
        return df['Volume'].sum()
    elif 'Date' in df.columns:
        return int(df['Volume'].mean())
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
    for file_path in os.listdir('stock_dfs'):
        tickers.append(file_path.replace('.csv',''))
    for ticker in tickers:
        vol = get_volume(ticker)
        if vol > volume:
            print('{} -> Volume: {}'.format(ticker, round(vol/volume,3)))
                
def visualize_data2():
    df = pd.read_csv('ibovespa_joined_closes.csv')
    df_corr = df.corr()
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
            if data1 >= 0.97 and index != index1 and check_volume([index,index1]):                
                print(('{} e {} fator de correlação: {}').format(index, index1, data1))
    

#visualize_data2()
list_tickets(10**7)                
