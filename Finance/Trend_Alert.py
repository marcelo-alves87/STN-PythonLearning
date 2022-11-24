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

BULLISH_TRENDS = 'Bullish_Trends.txt'
BEARISH_TRENDS = 'Bearish_Trends.txt'
FIBO_ALERT = "Fibo_Alert.txt"
MAIN_DF_FILE = 'main_df.pickle'
CONFIG_FILE = 'config.txt'
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
        fibo_alert = None
        config = None
        with open (BULLISH_TRENDS, 'rb') as f:
                bullish_trends = json.load(f)
        with open (BEARISH_TRENDS, 'rb') as f:
                bearish_trends = json.load(f)
        with open (FIBO_ALERT, 'rb') as f:
                fibo_alert = json.load(f)
        with open (CONFIG_FILE, 'rb') as f:
                config = json.load(f)        
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
         df_ticket = groups.loc[name][::-1]
         
         
         if isinstance(df_ticket, pd.DataFrame) and len(df_ticket.index) > 2:
             
             df_ticket.set_index('Data/Hora', inplace=True)
             df_ticket.sort_index(inplace=True)                    

             if df_ticket['low'][-2] >= df_ticket['low'][-3] and name not in bullish_trends:
                 bullish_trends[name] = df_ticket['low'][-3]
             elif name in bullish_trends:
                 if df_ticket['low'][-2] < df_ticket['low'][-3]:
                    level = bullish_trends[name]/df_ticket['high'][-3]
                    if level < config['THRESHOLD']:
                        fibo_alert[name] = [bullish_trends[name], df_ticket['high'][-3], 'ON']
                        bullish_trends.pop(name)
                    elif df_ticket['low'][-2] < bullish_trends[name]:
                       bullish_trends[name] = df_ticket['low'][-2]
                       
                                        
             if df_ticket['high'][-2] <= df_ticket['high'][-3] and name not in bearish_trends:
                 bearish_trends[name] = df_ticket['high'][-3]
             elif name in bearish_trends:
                 if df_ticket['high'][-2] > df_ticket['high'][-3]:
                    level = df_ticket['low'][-3]/bearish_trends[name]
                    if level < config['THRESHOLD']:                        
                       fibo_alert[name] = [bearish_trends[name], df_ticket['low'][-3], 'ON']
                       bearish_trends.pop(name)
                    elif df_ticket['high'][-2] > bearish_trends[name]:
                       bearish_trends[name] = df_ticket['high'][-2]                    
              
             fibo_alert = do_fibo_alert(fibo_alert, df_ticket, name, config)
             
        with open(BULLISH_TRENDS, 'w') as f:
              json.dump(bullish_trends, f)
        with open(BEARISH_TRENDS, 'w') as f:
              json.dump(bearish_trends, f)
        with open(FIBO_ALERT, 'w') as f:              
              json.dump(fibo_alert, f)         
        
        
        
def do_fibo_alert(fibo_alert, df, name, config):
     
     if name in fibo_alert:
       lvl100 = fibo_alert[name][0]
       lvl0 = fibo_alert[name][1]
       status = fibo_alert[name][2]
       
       if status == 'ON':                                 
         if lvl0 > lvl100:
            if df['high'][-1] > lvl0:
               fibo_alert[name] = [lvl100, df['high'][-1], 'ON']
            elif df['high'][-2] > lvl0:
               fibo_alert[name] = [lvl100, df['high'][-2], 'ON']   
            else:
               lvl328 = round(lvl0 - ((lvl0 - lvl100) * 32.8 / 100),2)
               lvl50 = round(lvl0 - ((lvl0 - lvl100) * 50 / 100),2)
               lvl618 = round(lvl0 - ((lvl0 - lvl100) * 61.8 / 100),2)

               levels = [lvl328, lvl50, lvl618]   
              
               for i in range(len(levels) - 1):
                  lvl_start = levels[i]
                  lvl_end = levels[i + 1]
                  if df['low'][-1] <= lvl_start and df['low'][-1] >= lvl_end - config['PRICE_OFFSET']:                     
                     fibo_alert[name] = [lvl100, lvl0, 'OFF']
                     break                    
         else:
            if df['low'][-1] < lvl0:
               fibo_alert[name] = [lvl100, df['low'][-1], 'ON']
            elif df['low'][-2] < lvl0:
               fibo_alert[name] = [lvl100, df['low'][-1], 'ON']   
            else:
               lvl328 = round(lvl0 + ((lvl100 - lvl0) * 32.8 / 100),2)
               lvl50 = round(lvl0 + ((lvl100 - lvl0) * 50 / 100),2)
               lvl618 = round(lvl0 + ((lvl100 - lvl0) * 61.8 / 100),2)

               levels = [lvl328, lvl50, lvl618]   
              
               for i in range(len(levels) - 1):
                  lvl_start = levels[i]
                  lvl_end = levels[i + 1]
                  if df['high'][-1] >= lvl_start and df['high'][-1] <= lvl_end + config['PRICE_OFFSET']:
                     fibo_alert[name] = [lvl100, lvl0, 'OFF']
                     break    
       elif status == 'OFF':
          print(df.index[-1],'********',name, '********', lvl100, lvl0, round(lvl100/lvl0, 2) if lvl0 > lvl100 else round(lvl0/lvl100, 2))
          if lvl0 > lvl100:
             tgt0 = round(lvl0,2)
             tgt0272 = round(lvl0 - ((lvl0 - lvl100) * -27.2 / 100),2)
             tgt0618 = round(lvl0 - ((lvl0 - lvl100) * -61.8 / 100),2)
             tgt1618 = round(lvl0 - ((lvl0 - lvl100) * -161.8 / 100),2)

             targets = [tgt0, tgt0272, tgt0618, tgt1618]
              
             for i,target in enumerate(targets):
               print('Target',i + 1,' : ',target)
                
          else:
             tgt0 = round(lvl0,2)
             tgt0272 = round(lvl0 + ((lvl100 - lvl0) * -27.2 / 100),2)
             tgt0618 = round(lvl0 + ((lvl100 - lvl0) * -61.8 / 100),2)
             tgt1618 = round(lvl0 + ((lvl100 - lvl0) * -161.8 / 100),2)

             targets = [tgt0, tgt0272, tgt0618, tgt1618]
              
             for i,target in enumerate(targets):
               print('Target',i + 1,' : ',target)
             
          
          fibo_alert[name] = [lvl100, lvl0, 'SBY']
     return fibo_alert        

                    
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
        
        df = df[df['Data/Hora'] > '10:00:00']
        
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
    time1 = main_df.index[0]
    last_time = main_df.index[-1]
    
    while time1 < last_time:

        df = main_df.reset_index()
        df = df[df['Data/Hora'] < time1]        
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)

        verify_trends(df)

        #time.sleep(1)       
        
        time1 += dt.timedelta(minutes = 5)

def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   with open(BULLISH_TRENDS, 'w') as f:
      json.dump(empty_json, f)
   with open(BEARISH_TRENDS, 'w') as f:
      json.dump(empty_json, f)
   with open(FIBO_ALERT, 'w') as f:
      json.dump(empty_json, f)   
      
reset(reset_main=True)
main()
#test()


