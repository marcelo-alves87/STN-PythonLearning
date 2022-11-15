import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pdb
import time
import datetime as dt
import os
import json
from selenium.common.exceptions import WebDriverException
import Utils as utils
import sys
import DayTrade as dtr
import datetime as dt
import pickle

THRESHOLD = 0.98
MAIN_DF_FILE = 'main_df.pickle'
URL = "https://rico.com.vc/"
bullish_trends = {}
bearish_trends = {}

def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def verify_trends(main_df):
    if not main_df.empty:
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
        
            df_ticket = groups.loc[name][::-1]
            if isinstance(df_ticket, pd.DataFrame) and len(df_ticket.index) > 2:
                df_ticket.set_index('Data/Hora', inplace=True)
                df_ticket.sort_index(inplace=True)                    

                if df_ticket['low'][-2] >= df_ticket['low'][-3] and name not in bullish_trends:
                    bullish_trends[name] = df_ticket['low'][-3]
                elif df_ticket['low'][-2] < df_ticket['low'][-3] and  name in bullish_trends:
                    level = bullish_trends[name]/df_ticket['high'][-3]
                    if level < THRESHOLD:
                        print(df_ticket.index[-1], '********** ' + name + ' ********* ', bullish_trends[name], df_ticket['high'][-3])
                        bullish_trends.pop(name)                
                    
                if df_ticket['high'][-2] <= df_ticket['high'][-3] and name not in bearish_trends:
                    bearish_trends[name] = df_ticket['high'][-3]
                elif df_ticket['high'][-2] > df_ticket['high'][-3] and name in bearish_trends:
                    level = df_ticket['low'][-3]/bearish_trends[name]
                    if level < THRESHOLD:
                        print(df_ticket.index[-1], '********** ' + name + ' ********* ', bearish_trends[name], df_ticket['low'][-3])
                        bearish_trends.pop(name)                                
            
                
def main():
    main_df = pd.DataFrame()
    if os.path.exists(MAIN_DF_FILE):
        main_df = pd.read_pickle(MAIN_DF_FILE)    
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Wait ...')
    driver.switch_to.window(driver.window_handles[1])
    print('Running ...')
    
    while(True):
        
        driver.execute_script("document.getElementById('app-menu').click()")
        html = get_page_source(driver)   
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 

        df = pd.read_html(str(tables[0]))[0]

        df = df[['Ativo','Máximo','Mínimo','Data/Hora','Último', 'Abertura']]

        df['Último'] = df['Último']/100
        df['Máximo'] = df['Máximo']/100
        df['Mínimo'] = df['Mínimo']/100
        df['Abertura'] = df['Abertura']/100
        
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
        df.set_index('Data/Hora',inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = pd.concat([main_df, df])
            main_df.to_pickle(MAIN_DF_FILE)

        verify_trends(main_df)
                               
        time.sleep(3)

def test():
    
    main_df = pd.read_pickle(MAIN_DF_FILE)
    time = main_df.index[0]
    last_time = main_df.index[-1]
    
    while time < last_time:

        df = main_df.reset_index()
        df = df[df['Data/Hora'] < time]        
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)
        
        verify_trends(df)
        
        time = time + dt.timedelta(minutes = 5)
main()
#test()


