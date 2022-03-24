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
import DayTrade as dtr
from selenium.common.exceptions import WebDriverException
import json
import Utils as utils

##139097
##
##window.localStorage.setItem('info',JSON.stringify(t))
##window.localStorage.setItem('data',JSON.stringify(i))
##window.localStorage.setItem('info2',a)
##window.localStorage.getItem('info')

MY_TICKETS = ['MGLU3', 'CSNA3', 'PETR4', 'BRFS3']
PICKLE_FILE = 'btc_tickers.plk'
URL = "https://rico.com.vc/arealogada/home-broker"

def datetime_localstorage(x):
   x = utils.convert_to_datetime(x)
   x = x - dt.timedelta(hours=6)
   return utils.convert_to_str(x)

def get_localstorage_(driver):
   try:
      info = json.loads(driver.execute_script("return window.localStorage.getItem(\'info\')"))
      data = json.loads(driver.execute_script("return window.localStorage.getItem(\'data\')"))
      info2 = driver.execute_script("return window.localStorage.getItem(\'info2\')")
      return info,data,info2
   except WebDriverException as e:
      time.sleep(1)
      return get_localstorage_(driver)
   
def get_localstorage(driver,tickets,period):
   for ticket in tickets:
      
      input('Do local storage for {} at each {}'.format(ticket,period))
      
      info, data, info2 = get_localstorage_(driver)
      
      df_data = pd.DataFrame(data['quotes'])
      
      df_data = df_data[['dtDateTime', 'nOpen', 'nMax', 'nMin', 'nClose','nVolume']]
      df_data.rename(columns={'dtDateTime': 'Datetime', 'nOpen': 'Open', 'nMax': 'High', 'nMin': 'Low', 'nClose' : 'Close', 'nVolume' : 'Volume'}, inplace=True)
      df_data['Adj Close'] = df_data['Close']
      df_data = df_data[['Datetime', 'Open', 'High', 'Low', 'Adj Close','Volume']]
      df_data['Datetime'] = df_data['Datetime'].apply(lambda x: x[:-5])
      df_data['Datetime'] = df_data['Datetime'].apply(lambda x: x.replace('T',' '))
      df_data['Datetime'] = df_data['Datetime'].apply(lambda x: datetime_localstorage(x))
      df_data.set_index('Datetime',inplace=True)
      ticker = info['strTicker']

      path = 'stock_dfs/' + ticker.upper() + '.csv'
      if os.path.exists(path):
         
         df1 = pd.read_csv(path)
         os.remove(path)
         df_data.reset_index(inplace=True)
         df_data = df_data[df_data['Datetime'] < df1['Datetime'][0]]
         
         df_data = pd.concat([df_data,df1])
         df_data.set_index('Datetime',inplace=True)
            
      df_data.to_csv(path) 
      
def convert_to_datetime_str(x):
   try:
       mytime = dt.datetime.strptime(x,'%H:%M:%S').time()
       date = dt.datetime.combine(dt.date.today(), mytime)
       return date.strftime("%Y-%m-%d %H:%M:%S")
   except:
       return np.NaN
        
def merge_free_float_with_btc():
    #Tickers that allow leverage and BTC
    df1 = dtr.get_leverage_btc()
    mask = df1['Papel'].isin(MY_TICKETS)
    df1 = df1[mask]
    df2 = dtr.get_free_float()
    df = pd.merge(df1, df2, on='Papel', how='outer')
    df.drop(['Acao', 'Tipo', 'Free Float'], 1, inplace=True)
    df = df[df['Lev.'].notna()]
    return df

def update_main_df():
    df_btc = merge_free_float_with_btc()
    if os.path.isfile(PICKLE_FILE):
        main_df = pd.read_pickle(PICKLE_FILE)
        main_df = pd.merge(main_df, df_btc, on='Papel', how='outer')
        main_df.drop(['Lev._x', 'Nome'], 1, inplace=True)
        main_df.rename(columns={'Lev._y': 'Lev.'}, inplace=True)
        main_df.dropna(inplace=True)
        main_df.to_pickle(PICKLE_FILE)    
    return df_btc                         

def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def scrap_rico():

    df_btc = update_main_df()


       
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

##    if os.path.exists(PICKLE_FILE):
##       os.remove(PICKLE_FILE)
##    get_localstorage(driver,df_btc['Papel'],'1min')
##    get_localstorage(driver,df_btc['Papel'],'5min')
    input('Wait ...')
    while(True):

        
        print('Reading, do not close ...')
      
        html = get_page_source(driver)   
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 
        
        df = pd.read_html(str(tables[0]))[0]

        if os.path.isfile(PICKLE_FILE): 
            main_df = pd.read_pickle(PICKLE_FILE)
        else:
            main_df = pd.DataFrame()
        
        df = df[['Ativo','Último','Abertura','Data/Hora', 'Financeiro', 'Mínimo', 'Máximo']]

        df['Último'] = df['Último']/100
        df['Máximo'] = df['Máximo']/100
        df['Mínimo'] = df['Mínimo']/100

        df = pd.merge(df_btc, df, left_on=df_btc["Papel"], right_on=df["Ativo"], how='left')
        df = df[['Papel', 'Lev.', 'Último', 'Data/Hora', 'Financeiro', 'Mínimo', 'Máximo', 'Abertura']]
        df = df.dropna()
        df.rename(columns={'Data/Hora': 'Hora', 'Financeiro': 'Volume'}, inplace=True)
        
        now = df['Hora'].iloc[-1]
        
        df['Hora'] = df['Hora'].apply(convert_to_datetime_str)
        df = df.dropna()
        
        if len(df) > 0:
            
            df = pd.concat([main_df, df]).reset_index(drop=True)

            for name, group in df.groupby(['Papel']):
            
               path = 'stock_dfs/' + name.upper() + '.csv'
               if os.path.exists(path):
                   
                   df1 = pd.read_csv(path)
                    
                   df1.rename(columns={'Datetime': 'Hora', 'Adj Close': 'Último'}, inplace=True)
                   df1['Papel'] = name
                   df1 = df1[['Papel','Hora','Último']]
                                         
                   df = pd.concat([df1, df])
                   df.fillna(0,inplace=True)
                   
                   os.remove(path)
               
            df.to_pickle(PICKLE_FILE) # where to save it usually as a .plk
            
        print('Read {}, sleeping now, CTRL + C to quit...'.format(now))
        time.sleep(3)


scrap_rico()

