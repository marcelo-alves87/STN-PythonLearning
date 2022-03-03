import datetime as dt
from datetime import date, timedelta, datetime
import timedelta
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import yfinance as yfin
import pdb
import DayTrade as dtr
import pdb 
yfin.pdr_override()


def fetch_ticker(ticker,start,tomorrow,period):
    try:
        df = web.get_data_yahoo(ticker + '.SA', start=start.strftime('%Y-%m-%d'), end=tomorrow.strftime('%Y-%m-%d'),interval=period)
        return df
    except:
        print(ticker,'não foi encontrado')


def get_data_from_yahoo(interval = 6, period = '1m', join = False, now = dt.date.today()):
    
    df = dtr.get_leverage_btc(False)
        
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    
    start =  now - dt.timedelta(days=interval)    
    tomorrow = now + dt.timedelta(days=1)    
    
    for i,row in df.iterrows():
        ticker = row['Papel']
        print(ticker)
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)) and not join:
            df = fetch_ticker(ticker, start, tomorrow, period)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))     
        elif join:            
            df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df1.set_index('Datetime',inplace=True)
            df2 = fetch_ticker(ticker, start, tomorrow, period)
            df3 = pd.concat([df2,df1])
            df3.to_csv('stock_dfs/{}.csv'.format(ticker))     
        else:
            print('Already have {}'.format(ticker))
  

#join = True, now = dt.datetime.strptime('2022-02-24','%Y-%m-%d')            
#get_data_from_yahoo()
get_data_from_yahoo(join = True, now = dt.datetime.strptime('2022-02-24','%Y-%m-%d')) 
