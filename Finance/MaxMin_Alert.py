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
THRESHOLD = .98
last_lvl = {}
price_alert = {}
black_list = []
INVESTMENT = 200

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
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual', 'Financeiro']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
           df_ticket = groups.loc[name][::-1]
         
           if isinstance(df_ticket, pd.DataFrame):

              df_ticket.set_index('Data/Hora',inplace=True)
              df_ticket.sort_index(inplace=True)
              
              if name not in last_lvl and df_ticket['Mínimo']['open'][-1] > df_ticket['Mínimo']['low'][-1] \
                 and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
                 last_lvl[name] = [df_ticket['Máximo']['high'][-1], 'Bearish'] 
                 notify(df_ticket.index[-1], name, 'Short', df_ticket['Máximo']['high'][-1], df_ticket['Mínimo']['open'][-1],\
                        df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'])
              elif name in last_lvl and last_lvl[name][1] == 'Bearish' and df_ticket['Último']['close'][-2] > last_lvl[name][0]:
                 last_lvl.pop(name)

              if name not in last_lvl and df_ticket['Máximo']['open'][-1] < df_ticket['Máximo']['high'][-1] \
                 and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
                 last_lvl[name] = [df_ticket['Mínimo']['low'][-1], 'Bullish']
                 notify(df_ticket.index[-1], name, 'Long', df_ticket['Máximo']['open'][-1], df_ticket['Mínimo']['low'][-1],\
                        df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'])
              elif name in last_lvl and last_lvl[name][1] == 'Bullish' and df_ticket['Último']['close'][-2] < last_lvl[name][0]:
                 last_lvl.pop(name)

              if name in price_alert:
                 if isinstance(price_alert[name], float):
                    price_alert[name] = [price_alert[name]]
                 if isinstance(price_alert[name], list):
                    for i in range(len(price_alert[name])):
                       price = price_alert[name][i]
                       if df_ticket['Último']['high'][-1] >= price and df_ticket['Último']['low'][-1] <= price:              
                          notify(df_ticket.index[-1], name, 'Alert', price, df_ticket['Último']['close'][-1],\
                             df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'], ignore_restrictions=True)
                          price_alert.pop(name) 
                          with open(PRICE_ALERT, 'w') as f:
                             json.dump(price_alert, f)
                          time.sleep(1)   
                          break   
                             

              
def get_status(variation):
   variation = variation.replace('%','')
   variation = variation.replace(',','.')
   variation = float(variation)
   if variation > 0:
      return [1,variation]
   elif variation < 0:
      return [-1,variation]
   else:
      return [0,variation]

def print_finance_(row):
   if isinstance(row, float):
      row = round(row,2)
      if row > 10 ** 9:
         row = row / 10 ** 9 
         row = '{} B'.format(row)
      elif row > 10 ** 6:
         row = row / 10 ** 6 
         row = '{} M'.format(row)
      elif row > 10 ** 3:
         row = row / 10 ** 3
         row = '{} k'.format(row)
      return row 

def print_finance(finance):
    accum = print_finance_(finance[-2])
    if len(finance) > 2:
      min = print_finance_(finance.diff()[-2])
    else:
      min = accum
    return accum, min

def cal_gross_value(type, lvl0, lvl100):
   if type == 'Short':
      lvlx = lvl100 - (lvl0 - lvl100)
      price = lvl100
   else:
      lvlx = lvl0 + (lvl0 - lvl100)
      price = lvl0
         
   leverage = INVESTMENT * 100
   volume = int(leverage/price)

   if type == 'Short':
      gross_value = (price - lvlx) * volume
   else:
      gross_value = (lvlx - price) * volume
   return round(gross_value,2)

def sound_alert():
   winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   time.sleep(1)
   
def notify(index, name, type, lvl0, lvl100, variation, finance, ignore_restrictions=False):
   var = get_status(variation)
   accum = print_finance(finance)[0]
   min = print_finance(finance)[1]
   if ignore_restrictions:
      print(index,'********',name, '********', type, lvl0, variation, accum, min)
      sound_alert()      
   elif 'k' not in accum and ((var[0] == 1 and type == 'Short') or (var[0] == -1 and type == 'Long')\
        or (var[0] == 1 and var[1] > 2.85 and var[1] < 4)):      
      print(index,'********',name, '********', type, lvl0, lvl100, round(lvl100/lvl0,3), variation, accum, min, cal_gross_value(type, lvl0, lvl100))
      sound_alert()

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

def main():
    main_df = pd.DataFrame()
    if os.path.exists(MAIN_DF_FILE):
        main_df = pd.read_pickle(MAIN_DF_FILE)    
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Waiting ...')
    #pdb.set_trace()
    driver.switch_to.window(driver.window_handles[1])
    print('Running ...')
    #insert_tickets(driver)
    while(True):

        
        driver.execute_script("document.getElementById('app-menu').click()")
        driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop = 0") 
        
        df = get_all_tickets_status(driver)
        
        df = df[['Ativo','Variação','Máximo','Mínimo','Data/Hora','Último', 'Abertura', 'Financeiro', 'Estado Atual']]

        df = df.drop(df[df['Ativo'] == 'IBOV'].index)

        df['Último'] = df['Último']/100
        df['Máximo'] = df['Máximo']/100
        df['Mínimo'] = df['Mínimo']/100
        df['Abertura'] = df['Abertura']/100
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row))  
        df['Financeiro'] = df['Financeiro'].astype(float) 
        df['Data/Hora'] = df['Data/Hora'].replace('-','00:00:00') 
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])

        start_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 10:00:00'
        end_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 18:00:00'

        df = df[df['Data/Hora'] >= start_date]
        df = df[df['Data/Hora'] <= end_date]

        
        df.set_index('Data/Hora',inplace=True)
        df.sort_index(inplace=True)
        
        if main_df.empty:
            main_df = df
        else:
            main_df = pd.concat([main_df, df])
            main_df.to_pickle(MAIN_DF_FILE)

    
        verify_trends(main_df)

        time.sleep(1)
  
def test():
    
    main_df = pd.read_pickle(MAIN_DF_FILE)
    time1 = main_df.index[0]
    last_time = main_df.index[-1]
    
    while time1 < last_time:

        df = main_df.reset_index()
        df = df[df['Data/Hora'] < time1]        
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row)) 
        df['Financeiro'] = df['Financeiro'].astype(float)
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
   
      
warnings.simplefilter(action='ignore', category=FutureWarning)
#reset(reset_main=True)
#main()
test()

