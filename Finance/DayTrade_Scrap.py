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


PICKLE_FILE = 'btc_tickers.plk'
URL = "https://rico.com.vc/arealogada/home-broker"


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


def scrap_rico():

    df_btc = update_main_df()

    
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL)

    input('Ready?')
    
    while(True):

        
        print('Reading, do not close ...')

        if os.path.isfile(PICKLE_FILE): 
            main_df = pd.read_pickle(PICKLE_FILE)
        else:
            main_df = pd.DataFrame()

        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 

        df = pd.read_html(str(tables[0]))[0]

        
        
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
                    
                   df1['Datetime'] = df1['Datetime'].apply(lambda x: x[:-6])
                   df1.rename(columns={'Datetime': 'Hora', 'Adj Close': 'Último'}, inplace=True)
                   df1['Papel'] = name
                   df1 = df1[['Papel','Hora','Último']]
                                         
                   df = pd.concat([df, df1])
                   df.fillna(0,inplace=True)
                   
                   os.remove(path)
               
            df.to_pickle(PICKLE_FILE) # where to save it usually as a .plk
            
        print('Read {}, sleeping now, CTRL + C to quit...'.format(now))
        time.sleep(5)


scrap_rico()

