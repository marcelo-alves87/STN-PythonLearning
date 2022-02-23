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





def get_data_from_yahoo(interval = 6, period = '1m'):
    
    df = dtr.get_leverage_btc(False)
        
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    now = dt.date.today()    
    start =  now - dt.timedelta(days=interval)    
    tomorrow = now + dt.timedelta(days=1)    
    
    for i,row in df.iterrows():
        ticker = row['Papel']
        print(ticker)
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            try:
                df = web.get_data_yahoo(ticker + '.SA', start=start.strftime('%Y-%m-%d'), end=tomorrow.strftime('%Y-%m-%d'),interval=period)
                df.to_csv('stock_dfs/{}.csv'.format(ticker))           
            except:
                print(ticker,'não foi encontrado')
        else:
            print('Already have {}'.format(ticker))
  

            

get_data_from_yahoo() 
