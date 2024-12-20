import threading
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
import shutil
import yfinance as yfin
import numpy as np
from pymongo import MongoClient

yfin.pdr_override()

pause_flag_file = "pause.flag"
scraper_paused = False
pause_lock = threading.Lock()
# inter ma alert

MAIN_DF_FILE = 'main_df.pickle'
STATUS_FILE = 'status.pickle'
PRICE_ALERT = 'Price_Alert.txt'
URL = "https://rico.com.vc/"
color = sys.stdout.shell
last_date = None
last_ibov_var = None
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
status = {}
price = {}
EXTERNAL_JSON = "PriceServer/btc-181123_2006-181124_0105.json"
client =  MongoClient("localhost", 27017)
db = client.mongodb
prices = db.prices

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

def strategy():
    global main_df
    group = []
    for file_path in os.listdir('stock_dfs'):
       name = file_path.replace('.csv','')
       if len(main_df[main_df['Ativo'] == name]) > 0:
          series = main_df[main_df['Ativo'] == name].iloc[-1]          
          price[name] = series['Último']
          myjson = { 'time' :  series.name.strftime('%Y-%m-%d %H:%M:%S'),\
                     'open' :  series['Último'],\
                     'high' : series['Último'],\
                     'low' :  series['Último'],\
                     'close' : series['Último'],\
                     'volume' : series['Financeiro'],\
                     'ativo' : name }
          group.append(myjson)
    df = pd.DataFrame(group)
    if not df.empty and 'time' in df.columns:
       df['time'] = pd.to_datetime(df['time'])
       prices.insert_many(df.to_dict('records'))    
         
def save_status():
   with open(STATUS_FILE, 'wb') as handle:
         pickle.dump(status, handle)
   time.sleep(1)
   
def sound_alert():
   winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   time.sleep(1)
 
def notify(index, name, var, type, mode=1):
   if mode == 1:
      alert_str = str(index) + ' ' + name + ' ' + '(' + str(var) + ')'
      print('************')
      if type == 'Bullish':
         color.write(alert_str,'STRING')
      elif type == 'Bearish':
         color.write(alert_str,'COMMENT')
      elif type == 'Alert':
         color.write(alert_str,'KEYWORD')   
      print('\n************')
      sound_alert()
   else:
      print("{} -> {} ({}) is {}".format(index, name, var, type))
   
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
   #while has_next:
   df = get_page_df(driver)
       #driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop += 3000")
   #if main_df is None:
   main_df = df
       #else:
       #   main_df = pd.concat([main_df, df])
       #   df2 = df[df['Ativo'] == 'YDUQ3']
       #   if not df2.empty:
       #      has_next = False
   
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

def format_ticket(ticket):
   ticket = ticket.split(' ')
   if len(ticket) == 2:
      ticket = ticket[1]
   else:
      ticket = ticket[0]
   return ticket

def do_scraping():
    main_df = pd.DataFrame()
    if os.path.exists(MAIN_DF_FILE):
       main_df = pd.read_pickle(MAIN_DF_FILE)    
        
    options_ = webdriver.ChromeOptions()
    options_.binary_location = "C:\\Users\\55819\\Downloads\\Chrome\\chrome-win64\\chrome-win64\\chrome.exe"
    options_.add_argument("--incognito")
    options_.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(executable_path=r"C:\\Users\\55819\\Downloads\\Chrome\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service,options=options_)
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

def save_csv_data():
   df = pd.DataFrame()
   prices.delete_many({})
   if os.path.exists('stock_dfs'):
      for file_path in os.listdir('stock_dfs'):
         name = file_path.replace('.csv','')
         df1 = pd.read_csv('stock_dfs/{}.csv'.format(name))
         df1['ativo'] = name         
         df1['Datetime'] = pd.to_datetime(df1['Datetime'])
         df1.rename(columns={'Datetime': 'time', 'Open' : 'open', 'High' : 'high', 'Low' : 'low', 'Close' : 'close', 'Volume' : 'volume' }, inplace=True)
         df = pd.concat([df, df1])                  
   prices.insert_many(df.to_dict('records'))      

def main():
    global main_df
    main_df, driver = do_scraping()    
    #pdb.set_trace()
    #insert_tickets(driver)
    while(True):
        with pause_lock:
            if scraper_paused:
                print("Scraper waiting...")
                time.sleep(1)
                continue
        try:
           driver.execute_script("document.getElementById('app-menu').click()")
        except:
           print('Catched Exception ...')
           time.sleep(3)
           
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
           
           strategy()

        time.sleep(0.1)

def format_date(row):
   return row.replace('-03:00','')

def update(ticket):
   
   data = []
   if os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      df4 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
      for index,row in df4.iterrows():
         date = dt.datetime.strptime(row['Datetime'], '%Y-%m-%d %H:%M:%S')
         _data = {'Data/Hora' : (date - dt.timedelta(minutes = 0)).strftime('%Y-%m-%d %H:%M:%S'), 'Ativo' : ticket, 'Variação' : '0,00%',\
                      'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Open'],2),\
                      'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'}
         data.append(_data)
         data.append({'Data/Hora' : (date + dt.timedelta(minutes = 1)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                      'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Low'],2),\
                      'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
         data.append({'Data/Hora' : (date + dt.timedelta(minutes = 2)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                      'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['High'],2),\
                      'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
         data.append({'Data/Hora' : (date + dt.timedelta(minutes = 3)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                      'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) ,\
                      'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
   df4 =  pd.DataFrame(data)
   if not df4.empty:
      df4['Data/Hora'] = pd.to_datetime(df4['Data/Hora'])
      df4.set_index('Data/Hora', inplace=True)
      df4.sort_index(inplace=True)
      df4 = df4[df4.index > df4.index[0].strftime('%Y-%m-%d 10:00:00')]
      df3 = df4[df4.index < df4.index[0].strftime('%Y-%m-%d 18:00:00')]
      df5 = df4[df4.index > df4.index[-1].strftime('%Y-%m-%d 10:00:00')]
      df = pd.concat([df3, df5])
   return df4

def get_data(reset):
   #addPriceSerieEntityByDataSerieHistory
   # 1 min
   # mydata = t.filter((item) => item.dtDateTime <  new Date('2024-04-01'));

   if reset and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')      
      time.sleep(1)
      os.makedirs('stock_dfs')   
   main_df, driver = do_scraping()
   main_df = get_all_tickets_status(driver)
   tickets = main_df['Ativo'].values
   for ticket in tickets:
      if ticket != 'IBOV':
         input('Waiting for mydata of {} ...'.format(ticket))
         length = driver.execute_script("return mydata.length")
         data = []
         for i in range(length):
            print(i)
            
            date_str = driver.execute_script("return mydata[" + str(i) +"].dtDateTime.toLocaleString()")
            date = dt.datetime.strptime(date_str, '%d/%m/%Y, %H:%M:%S')

            n_open = driver.execute_script("return mydata[" + str(i) +"].nOpen")
           
            n_max = driver.execute_script("return mydata[" + str(i) +"].nMax")
           
            n_min = driver.execute_script("return mydata[" + str(i) +"].nMin")
            
            n_close = driver.execute_script("return mydata[" + str(i) +"].nClose")

            n_quantity = driver.execute_script("return mydata[" + str(i) +"].nQuantity")
           
            data.append({'Datetime' : date, 'Open' : n_open, 'High' : n_max, 'Low' : n_min, 'Close' : n_close, 'Volume' : n_quantity })
         df = pd.DataFrame(data)
         df['Datetime'] = df['Datetime'] - dt.timedelta(hours = 3)
         if not os.path.exists('stock_dfs'):
            os.makedirs('stock_dfs')
         if os.path.exists('stock_dfs/{}.csv'.format(ticket)):
            df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
            df1 = df1[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df = pd.concat([df1, df])
            df.to_csv('stock_dfs/{}.csv'.format(ticket), mode='w+')           
         else:
            df.to_csv('stock_dfs/{}.csv'.format(ticket))           
   time.sleep(1)
   save_csv_data()
   
def reset(reset_main):
   empty_json = {}
   if reset_main:
      if os.path.exists(MAIN_DF_FILE):
         os.remove(MAIN_DF_FILE)
      if os.path.exists(STATUS_FILE):   
         os.remove(STATUS_FILE)
      with open(PRICE_ALERT, 'w') as f:
         json.dump(empty_json, f)   


def check_pause():
    """Check if the pause flag file exists and pause the scraper if necessary."""
    global scraper_paused
    while True:
        if os.path.exists(pause_flag_file):
            with pause_lock:
                scraper_paused = True
            print("Scraping paused due to flag.")
        else:
            with pause_lock:
                scraper_paused = False
            #print("Scraping resumed.")
        time.sleep(5)  # Check every 5 seconds
   
         
warnings.simplefilter(action='ignore')
reset(reset_main=True)

#get_data(reset=True)

flag_monitor_thread = threading.Thread(target=check_pause)
scraping_thread = threading.Thread(target=main)

flag_monitor_thread.start()
scraping_thread.start()

# Keep the main program running
flag_monitor_thread.join()
scraping_thread.join()

