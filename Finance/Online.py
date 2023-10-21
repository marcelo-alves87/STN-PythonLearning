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
import pandas_datareader.data as web

MAIN_DF_FILE = 'main_df.pickle'
STATUS_FILE = 'status.pickle'
URL = "https://rico.com.vc/"
color = sys.stdout.shell
last_date = None
last_ibov_var = None
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
status = {}

def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def get_page_df(driver):
   html = get_page_source(driver)
   soup = BeautifulSoup(html, features='lxml')
   tables = soup.find_all('table', class_='nelo-table-group')
   df = pd.read_html(str(tables[0]))[0]
   df.dropna(inplace=True)
   return df

def strategy(main_df):
    global status
    if not main_df.empty:
        if os.path.exists(STATUS_FILE): 
           with open(STATUS_FILE, 'rb') as handle:
              status = pickle.load(handle)
               
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual', 'Financeiro']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
           df_ticket = groups.loc[name][::-1]
           df_ticket.set_index('Data/Hora',inplace=True)
           df_ticket.sort_index(inplace=True)
           verify_ma(name, df_ticket, status)
           
def verify_ma(name, df_ticket, status):
   
   if isinstance(df_ticket, pd.DataFrame) and len(df_ticket) > 1:

      df1 = df_ticket['Último']
      df1['EMA_1'] = df1['close'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
      df1['EMA_2'] = df1['close'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

      if df1['EMA_1'][-1] > df1['EMA_2'][-1] and\
         name not in status:
         status[name] = 'Bullish'
         save_status()
      elif df1['EMA_1'][-1] < df1['EMA_2'][-1] and\
         name not in status:
         status[name] = 'Bearish'
         save_status()
      elif df1['EMA_1'][-1] > df1['EMA_2'][-1] and\
         status[name] == 'Bearish':
         notify(df1.index[-1], name)
         status[name] = 'Bullish'
         save_status()
      elif df1['EMA_1'][-1] < df1['EMA_2'][-1] and\
         status[name] == 'Bullish':
         notify(df1.index[-1], name)
         status[name] = 'Bearish'   
         save_status()
         
def save_status():
   with open(STATUS_FILE, 'wb') as handle:
         pickle.dump(status, handle)
   time.sleep(1)
   
def sound_alert():
   winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   time.sleep(1)
 
def notify(index, name):
   color.write(index + ' ' + name,'DEFINITION')
   sound_alert()
   
   
def handle_finance(row):   
   if isinstance(row, float):
      return row
   elif isinstance(row, int):
      return float(row)
   else:
      row = row.replace('.','')
      row = row.replace(',','')
      row = row.replace('-','')
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

      if not isinstance(row, float):
         row = 0
         
      return row

def handle_price(row):
   if isinstance(row, float):
      row = str(row)
   
   if ',' in row:
      row = row.replace('.','').replace(',','.')   
   else:
      if '.0' == row[-2:]:
         row = row.replace('.0','')         
      elif '.' in row:
         row = row.replace('.','')         
      row = row[:-2] + '.' + row[-2:]
   return float(row)
      
def get_tickets():
   data = []
   data.append('IBOV')
   with open("Tickets.txt") as file:
    for line in file:
        ticket = line.rstrip() 
        if '11' not in ticket:
           data.append(ticket)
   return data
     
# You have to return to the browser quickly, and do nothing until the end of the inserting.   
def insert_tickets(driver):
   time.sleep(5)
   tickets = get_tickets()
   for ticket in tickets:
      if '11' not in ticket:
         print('Inserting ' + ticket + ' ...\n')
         time.sleep(1)
         driver.execute_script("document.querySelector('.nelo-dialog-titlebar-buttons__button--add-button').click()")
         time.sleep(2)
         typewrite(ticket)
         time.sleep(2)
         found = driver.execute_script("return document.querySelector('.tickerform-component-results').getElementsByTagName(\"li\").length")
         if found > 0:
            press('down')
            time.sleep(1)
            press('enter')
            time.sleep(1)
            verify_ticket_finance(ticket, driver)
            time.sleep(1)
         else:   
            press('esc')

def verify_ticket_finance(ticket, driver):
   df = get_page_df(driver)
   df = df[df['Ativo'] == ticket]
   if not df.empty and 'Financeiro' in df.columns:
      str1 = df[df['Ativo'] == ticket]['Financeiro'].values[0]
      if 'M' not in str1 and 'B' not in str1:         
         driver.execute_script("document.querySelectorAll('[id^=Rectangle_983--19]')[" + str(df.index[0]) + "].parentNode.parentNode.click()")
      
def get_all_tickets_status(driver):
   main_df = None
   has_next = True
   while has_next:
       df = get_page_df(driver)
       driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop += 3000")
       if main_df is None:
          main_df = df
       else:
          main_df = pd.concat([main_df, df])
          df2 = df[df['Ativo'] == 'YDUQ3']
          if not df2.empty:
             has_next = False
   
   global last_date, last_ibov_var
   now = dt.datetime.today()

   df_ativo = main_df['Ativo']
   df_ativo = df_ativo.reset_index()
   df_ativo = df_ativo.set_index('Ativo')
   df_ativo = df_ativo.drop_duplicates()
   
   
   if last_date is None:
      print('Read {} tickets at {}.'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S')))
   else:
      str1 = ''
      if last_ibov_var is not None:
         str1 = last_ibov_var
      secs = (now - last_date).seconds
      if secs >= 60:
         print('Read {} tickets at {} after {} min {} secs. IBOV ({}).'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S'),secs//60,secs%60, str1))
      else:
         print('Read {} tickets at {} after {} secs. IBOV ({}).'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S'),secs, str1))

         

   last_date = dt.datetime.today()
   return main_df

def do_scraping():
    main_df = pd.DataFrame()
    if os.path.exists(MAIN_DF_FILE):
       main_df = pd.read_pickle(MAIN_DF_FILE)    
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Waiting ...')
    tabs_size = len(driver.window_handles)
    for i in range(tabs_size):
       driver.switch_to.window(driver.window_handles[i])
       try:
          driver.execute_script("document.getElementById('app-menu').click()")
          break
       except:
          pass
    print('Running ...')
    return main_df, driver

def main(update_tickets):
    main_df, driver = do_scraping()  
    #insert_tickets(driver)
    while(True):

        try:
           driver.execute_script("document.getElementById('app-menu').click()")
        except:
           input('Catched Exception ...')
        driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop = 0") 
        
        df = get_all_tickets_status(driver)
        
        df = df[['Ativo','Variação','Máximo','Mínimo','Data/Hora','Último', 'Abertura', 'Financeiro', 'Estado Atual']]
        
        df['Último'] = df['Último'].apply(lambda row : handle_price(row)) 
        df['Máximo'] = df['Máximo'].apply(lambda row : handle_price(row)) 
        df['Mínimo'] = df['Mínimo'].apply(lambda row : handle_price(row))    
        df['Abertura'] = df['Abertura'].apply(lambda row : handle_price(row))    
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row))  
        df['Financeiro'] = df['Financeiro'].astype(float) 
        df['Data/Hora'] = df['Data/Hora'].replace('-','00:00:00') 
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], dayfirst=True)

        start_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 10:00:00'
        end_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 18:00:00'

        df = df[df['Data/Hora'] >= start_date]
        df = df[df['Data/Hora'] <= end_date]

        
        df.set_index('Data/Hora',inplace=True)
        df.sort_index(inplace=True)
        df = df[df.index >= dt.datetime.today().strftime('%Y-%m-%d')] 

        if main_df.empty:
           main_df = df         
        else:
           main_df = pd.concat([main_df, df])
           main_df.reset_index(inplace=True)
           main_df.set_index(['Data/Hora', 'Ativo'], inplace=True)
           main_df.drop_duplicates(inplace=True)
           main_df.reset_index(inplace=True)
           main_df.set_index('Data/Hora', inplace=True)            
           main_df.to_pickle(MAIN_DF_FILE)
           
           strategy(main_df)

        time.sleep(1)

def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   if reset_main and os.path.exists(STATUS_FILE):   
      os.remove(STATUS_FILE)
   
      
warnings.simplefilter(action='ignore')
reset(reset_main=True)
main()
