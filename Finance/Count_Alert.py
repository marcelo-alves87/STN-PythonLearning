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
import datetime as dt
import pickle
import winsound
from pyautogui import press, typewrite
import warnings



MAIN_DF_FILE = 'main_df.pickle'
PRICE_ALERT = 'Price_Alert.txt'
URL = "https://rico.com.vc/"
last_lvl = {}
price_alert = {}
black_list = []
lvls = [0,23.6,32.8,50,61.8,78.6, 100]
count = {}

def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def verify_trends(main_df):
    
    if not main_df.empty:
        
        with open (PRICE_ALERT, 'rb') as f:
           price_alert = json.load(f)
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
         df_ticket = groups.loc[name][::-1]
         
         if isinstance(df_ticket, pd.DataFrame) and len(df_ticket.index) > 2:
           
           df_ticket.set_index('Data/Hora',inplace=True)
           df_ticket.sort_index(inplace=True)

           if name not in last_lvl and df_ticket['Mínimo']['low'][-2]/df_ticket['Máximo']['high'][-2] < 0.987:
              last_lvl[name] = [df_ticket['Mínimo']['low'][-2], df_ticket['Máximo']['high'][-2]]
           elif name in last_lvl:
              bull_fibo = get_fibo(last_lvl[name][1],last_lvl[name][0])
              for i in range(len(bull_fibo) - 1):
                if df_ticket['Último']['high'][-2] > bull_fibo[lvls[i]] \
                   and df_ticket['Último']['high'][-2] <= bull_fibo[lvls[i + 1]]:
                      insert_count(lvls[i + 1], name, df_ticket.index[-2], df_ticket['Variação']['close'][-2], 'Bullish')
              bear_fibo = get_fibo(last_lvl[name][0],last_lvl[name][1])
              for i in range(len(bear_fibo) - 1):
                if df_ticket['Último']['low'][-2] < bear_fibo[lvls[i]] \
                   and df_ticket['Último']['low'][-2] >= bear_fibo[lvls[i + 1]]:
                      insert_count(lvls[i + 1], name, df_ticket.index[-2], df_ticket['Variação']['close'][-2], 'Bearish')

def insert_count(lvl, name, time, variation, type):
   if lvl in count and name not in count[lvl]:
      count[lvl].append([name, time, variation, type])
   else:
      count[lvl] = [name, time, variation, type]
   
      
def get_status(variation):
   variation = variation.replace('%','')
   variation = variation.replace(',','.')
   variation = float(variation)
   if variation > 0:
      return 1
   elif variation < 0:
      return -1
   else:
      return 0

def handle_finance(row):   
   if isinstance(row, float):
      return row
   else:
      row = row.replace('.','')
      row = row.replace(',','')
      row = row[:-3] + '.' + row[-3:]
      if 'k' in row:
         row = float(row.replace('k',''))
         row = row * 10**3
      elif 'M' in row:
         row = float(row.replace('M',''))
         row = row * 10**6
      elif 'B' in row:
         row = float(row.replace('B',''))
         row = row * 10**9   
      return row

def get_tickets():
   data = []
   f = open("Tickets.txt", "r")
   for line in f:
      data.append(f.readline().rstrip())
   f.close()
   return data

  
# You have to return to the browser quickly, and do nothing until the end of the inserting.   
def insert_tickets(driver):
   time.sleep(5)
   tickets = get_tickets()
   for ticket in tickets:
      time.sleep(1)
      driver.execute_script("document.querySelector('.nelo-dialog-titlebar-buttons__button--cross-button').click()")
      time.sleep(2)
      typewrite(ticket)
      time.sleep(2)
      found = driver.execute_script("return document.querySelector('.tickerform-component-results').getElementsByTagName(\"li\").length")
      if found > 0:
         press('down')
         time.sleep(1)
         press('enter')
      else:   
         press('esc')

def get_all_tickets_status(driver):
   main_df = None
   has_next = True
   while has_next:
       html = get_page_source(driver)   
       soup = BeautifulSoup(html, features='lxml')
       tables = soup.find_all('table', class_='nelo-table-group') 
       df = pd.read_html(str(tables[0]))[0]
       df.dropna(inplace=True)
       driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop += 100")
       if main_df is None:
          main_df = df
       else:
          df2 = df[df['Ativo'].isin(main_df['Ativo']) == False]
          if df2.empty:
             has_next = False
          else:
             main_df = pd.concat([main_df, df2])
   return main_df

def test():
    
    main_df = pd.read_pickle(MAIN_DF_FILE)
    time1 = main_df.index[0]
    last_time = main_df.index[-1]
    
    while time1 < last_time:

        df = main_df.reset_index()
        df = df[df['Data/Hora'] < time1]        
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row)) 
        
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)

        
        verify_trends(df)

        #time.sleep(1)
        time1 += dt.timedelta(minutes = 5)

    

def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   with open(PRICE_ALERT, 'w') as f:
      json.dump(empty_json, f)

def get_fibo(lvl0, lvl100):
   diff = lvl0 - lvl100
   dict = {}
   for lvl in lvls:
      dict[lvl] = round(lvl0 + ((diff) * lvl / 100),2)
   return dict
      
warnings.simplefilter(action='ignore', category=FutureWarning)
reset(reset_main=False)
#main()
test()
#count[78.6]
pdb.set_trace()

