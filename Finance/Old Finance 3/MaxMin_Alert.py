import pandas as pd
import requests
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
import math


MAIN_DF_FILE = 'main_df.pickle'
PRICE_ALERT = 'Price_Alert.txt'
URL = "https://rico.com.vc/"
THRESHOLD = 1
TIME_THRESHOLD = 15
price_alert = {}
black_list = []
color = sys.stdout.shell
last_date = None
last_ibov_var = None

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

def verify_trends(main_df):
    
    if not main_df.empty:

        with open (PRICE_ALERT, 'rb') as f:
           price_alert = json.load(f)
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual', 'Financeiro']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
           df_ticket = groups.loc[name][::-1]
           verify_df(name, df_ticket) 
           
def verify_df(name, df_ticket):
   if isinstance(df_ticket, pd.DataFrame):
            
        df_ticket.set_index('Data/Hora',inplace=True)
        df_ticket.sort_index(inplace=True)

        if name == 'IBOV':
           global last_ibov_var                 
           last_ibov_var = df_ticket['Variação']['close'][-1]                 
        else:
              
           #Strategy 1 - Wait for the pull-back
           
           min = df_ticket['Último']['close'].min()
           max = df_ticket['Último']['close'].max()
           time_min = df_ticket[df_ticket['Último']['close'] == min].index[0]
           time_max = df_ticket[df_ticket['Último']['close'] == max].index[0]


           has_red = df_ticket['Último'][df_ticket['Último']['open'] - df_ticket['Último']['close'] > 0.01].any().any()
           has_green = df_ticket['Último'][df_ticket['Último']['close'] - df_ticket['Último']['open'] > 0.01].any().any()

           
           if name not in black_list and min/max < THRESHOLD:
              last_var = get_status(df_ticket['Variação']['close'][-1])

              if time_max > time_min and not has_red:                    
                 time_diff = (time_max - time_min).seconds//60                    
                 if time_diff >= TIME_THRESHOLD:                       
                    notify(df_ticket.index[-1], name, df_ticket['Último']['close'][-1], time_diff, 'Bullish', min/max, df_ticket['Variação'], df_ticket['Financeiro']['close'])                                               
              elif time_max < time_min and not has_green:                    
                 time_diff = (time_min - time_max).seconds//60
                 if time_diff >= TIME_THRESHOLD:
                    notify(df_ticket.index[-1], name,  df_ticket['Último']['close'][-1], time_diff, 'Bearish', min/max, df_ticket['Variação'], df_ticket['Financeiro']['close'])  

   
           # Price Alert            
           if name in price_alert:
              if isinstance(price_alert[name], float):
                 price_alert[name] = [price_alert[name]]
              if isinstance(price_alert[name], list):
                 for i in range(len(price_alert[name])):
                    price = price_alert[name][i]
                    if df_ticket['Último']['high'][-1] >= price and df_ticket['Último']['low'][-1] <= price:              
                       notify(df_ticket.index[-1], name, df_ticket['Último']['close'][-1], time_diff, 'Alert', 1, df_ticket['Variação'],\
                              df_ticket['Financeiro']['close'], ignore_restrictions=True)
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
      else:
         row = '{}'.format(row)
      return row 

def print_finance(finance):
    accum = print_finance_(finance[-2])
    if len(finance) > 2:
      min = print_finance_(finance.diff()[-2])
    else:
      min = accum
    return accum, min

def sound_alert():
   winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   time.sleep(1)
 
def notify(index, name, price, time_diff, type, ratio, variation, finance, ignore_restrictions=False):
   black_list.append(name)
   accum = print_finance(finance)[0]
   min = print_finance(finance)[1]
   last_variation = variation.loc[variation.index[-1]]['close']
   str1 =  (index,'********',name, '********', price, str(time_diff) + ' mins ', type, round(ratio,3), last_variation, accum, min, '\n')
   try:
      var_index = variation.loc[variation.index[-1] - dt.timedelta(minutes = TIME_THRESHOLD)]      
   except:
      var_index = variation.iloc[0]     
   first_variation = get_status(var_index['close'])
   if ignore_restrictions:
      color.write(str1,'DEFINITION')
      sound_alert()
   elif isinstance(accum, str) and 'M' in accum and first_variation[0] == 1 and type == 'Bearish':      
      color.write(str1,'COMMENT')
      sound_alert()
   elif isinstance(accum, str) and 'M' in accum and type == 'Bearish':      
      color.write(str1,'SYNC')
      sound_alert()   
   elif isinstance(accum, str) and 'M' in accum:         
      color.write(str1,'STRING')
      
    
   
def handle_finance(row):   
   if isinstance(row, float):
      return row
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
        data.append(line.rstrip())
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
    ser = Service(r"Utils/chromedriver.exe")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    #driver = webdriver.Chrome(service=ser,options=options)
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

def main():
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

        
        if main_df.empty:
            main_df = df
        else:
            
            main_df = pd.concat([main_df, df])
            main_df.reset_index(inplace=True)
            main_df.set_index(['Data/Hora', 'Ativo'], inplace=True)
            main_df.drop_duplicates(inplace=True)
            main_df.reset_index(inplace=True)
            main_df.set_index('Data/Hora', inplace=True)            
            main_df.to_pickle(MAIN_DF_FILE, protocol=2)

    
        verify_trends(main_df)

        time.sleep(1)

def iterate(ticket):
    main_df = pd.read_pickle(MAIN_DF_FILE)
    for index,row in main_df.iterrows():
       if row['Ativo'] == ticket:
          print(index,row['Último'],row['Variação'])

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
##
##

def test_ticket(ticket):
   df = pd.read_pickle(ticket + '.pickle')
   df['Ativo'] = ticket
   df['Último2'] = df['Último'] 
   df = df.set_index('Data/Hora')
   groups = df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último' , 'Último2']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
   groups.reset_index(['Data/Hora'],inplace=True)
   for name in groups.index.unique():
      df_ticket = groups.loc[name][0::]
      time1 = df_ticket['Data/Hora'][0]
      last_time = df_ticket['Data/Hora'][-1]
      while time1 <= last_time:
         df = df_ticket[df_ticket['Data/Hora'] <= time1]
         verify_df(name, df)
         time1 += dt.timedelta(minutes = 5)

def get_data(ticket):
   #addPriceSerieEntityByDataSerieHistory
   # 5 min
   #mydata = e
   main_df, driver = do_scraping()
   input('Waiting for mydata ...')
   length = driver.execute_script("return mydata.length")
   data = []
   for i in range(length):
      print(i)
      
      date_str = driver.execute_script("return mydata[" + str(i) +"].dtDateTime.toLocaleString()")
      date = dt.datetime.strptime(date_str, '%d/%m/%Y, %H:%M:%S')

      n_open = driver.execute_script("return mydata[" + str(i) +"].nOpen")
      data.append({'Último' : n_open, 'Data/Hora' : date})
      

      n_max = driver.execute_script("return mydata[" + str(i) +"].nMax")
      date += dt.timedelta(minutes = 1)  
      data.append({'Último' : n_max, 'Data/Hora' : date})

      n_min = driver.execute_script("return mydata[" + str(i) +"].nMin")
      date += dt.timedelta(minutes = 1)  
      data.append({'Último' : n_min, 'Data/Hora' : date})
      
      n_close = driver.execute_script("return mydata[" + str(i) +"].nClose")      
      date += dt.timedelta(minutes = 1)  
      data.append({'Último' : n_close, 'Data/Hora' : date})
   df = pd.DataFrame(data)
   df['Data/Hora'] = df['Data/Hora'] - dt.timedelta(hours = 3)
   df.to_pickle(ticket + '.pickle', protocol=2)
      
   
def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   with open(PRICE_ALERT, 'w') as f:
      json.dump(empty_json, f)
   
      
warnings.simplefilter(action='ignore', category=FutureWarning)
reset(reset_main=True)
main()
#test()
#iterate('PETZ3')
#get_data('PETZ3')
#test_ticket('PETZ3')
