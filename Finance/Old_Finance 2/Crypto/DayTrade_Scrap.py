import tabula
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pdb
import time
import datetime as dt
import os
import pickle
import numpy as np
import pandas_datareader.data as web
import yfinance as yfin
yfin.pdr_override()


PICKLE_FILE = 'btc_cryptos.plk'
URL = "https://www.binance.com/pt-BR/markets/spot-BUSD"

def convert_to_float(x):
    x = x.replace('.','')
    x = float(x.replace(',','.'))
    return x

def convert_vol_to_float(x):
    if x[-1].isalpha():    
        if x[-1] == 'k':
            exp = 3
            vol = x[:-1]
        elif x[-1] == 'M':
            exp = 6
            vol = x[:-1]
        elif x[-1] == 'B':
            exp = 9
            vol = x[:-1]
        return convert_to_float(vol) * 10 ** exp    
    else:
        return convert_to_float(x)

def fetch_ticker(ticker,start,tomorrow,period):
    try:
        df = web.get_data_yahoo(ticker + '-USD', start=start.strftime('%Y-%m-%d'), end=tomorrow.strftime('%Y-%m-%d'),interval=period)
        df.set_index(pd.to_datetime(df.index.values) - pd.Timedelta(hours=3),inplace=True)
        return df
    except:
        print(ticker,'not found.')
     
def get_data_from_yahoo(interval = 5, period = '1m', join = False, now = dt.date.today()):
    
    tickers = scrap_binance(return_tickets=True)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    
    start =  now - dt.timedelta(days=interval)    
    tomorrow = now + dt.timedelta(days=1)    
    
    for ticker in tickers:
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
     
def scrap_binance(return_tickets=False):

    
    if os.path.exists(PICKLE_FILE):
        os.remove(PICKLE_FILE)
        
    df = pd.DataFrame()  
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    
    driver = webdriver.Chrome(executable_path=r"../Utils/chromedriver.exe",options=options)
    driver.get(URL)
    
    if return_tickets:
        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        tables = soup.find_all('div', class_='css-vlibs4')
        tickets = []
        for table in tables:               
            tickets.append(table.find('div', {'class': 'css-17wnpgm'}).text)
        return tickets
    
    else:
        
        while(True):
            print('Reading, do not quit ...')
            html = driver.page_source
            soup = BeautifulSoup(html, features='lxml')
            tables = soup.find_all('div', class_='css-vlibs4')
            
            for table in tables:
               
               name = table.find('div', {'class': 'css-17wnpgm'}).text

               price = table.find('div', {'class': 'css-1r1yofv'}).text           
               price = convert_to_float(price.split('/')[0])
               
               var = table.find('div', {'class': 'css-1vefg8'})
               if var is None:
                  var = table.find('div', {'class': 'css-131bcdq'})
               var = var.text
               
               max_min = table.find_all('div', {'class': 'css-102bt5g'})[0].text
               maximum = convert_to_float(max_min.split('/')[0])
               minimum = convert_to_float(max_min.split('/')[1])

               vol = table.find_all('div', {'class': 'css-102bt5g'})[1].text
               vol = convert_vol_to_float(vol)
               now = dt.datetime.now()
               df1 = { 'Date' : now, 'Ticket' : name, 'Price' : price, 'Var.' : var, 'Max Price' : maximum, 'Minimum Price': minimum, 'Volume' : vol }
               df1 = pd.DataFrame([df1])
                
               
               path = 'stock_dfs/' + name.upper() + '.csv'
               if os.path.exists(path):
                   
                   df1 = pd.read_csv(path)                   
                   df1.reset_index(inplace=True)
                   df1.rename(columns={'Unnamed: 0': 'Date', 'Adj Close': 'Price'}, inplace=True)
                   df1['Ticket'] = name.upper()
                   df1 = df1[['Date','Ticket','Price','Volume']]                                      
                   df.fillna(0,inplace=True)                   
                   os.remove(path)
                   
               df = pd.concat([df1, df])
                   
            df.to_pickle(PICKLE_FILE) # where to save it usually as a .plk            
            print('Read {}, sleeping now, CTRL + C to quit...'.format(now))
            time.sleep(3)
        
get_data_from_yahoo()        
        
scrap_binance()

        



  



