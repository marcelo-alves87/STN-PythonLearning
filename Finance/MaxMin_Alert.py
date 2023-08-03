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



MAIN_DF_FILE = 'main_df.pickle'
PRICE_ALERT = 'Price_Alert.txt'
URL = "https://rico.com.vc/"
THRESHOLD = 1
TIME_THRESHOLD = 25
price_alert = {}
black_list = []
color = sys.stdout.shell
last_date = None

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
         
           if isinstance(df_ticket, pd.DataFrame):

              df_ticket.set_index('Data/Hora',inplace=True)
              df_ticket.sort_index(inplace=True)

              min = df_ticket['Mínimo']['low'].min()
              max = df_ticket['Máximo']['high'].max()
              time_min = df_ticket[df_ticket['Mínimo']['low'] == min].index[0]
              time_max = df_ticket[df_ticket['Máximo']['high'] == max].index[0]


              #Strategy 1 - Highering/lowering prices for a long time
              #has_bulish, has_bearish = it_has(name, df_ticket, time_min, time_max)
              has_red = df_ticket['Último'][df_ticket['Último']['open'] - df_ticket['Último']['close'] > 0.01].any().any()
              has_green = df_ticket['Último'][df_ticket['Último']['close'] - df_ticket['Último']['open'] > 0.01].any().any()
              

              if name not in black_list and min/max < THRESHOLD:
                 last_var = get_status(df_ticket['Variação']['close'][-1])
                 
                
##                 if time_max > time_min:
##                    time_diff = (time_max - time_min).seconds//60
##                    min_var = get_status(df_ticket.loc[time_min]['Variação']['close'])
##                    if last_var[0] == -1:
##                       notify(df_ticket.index[-1], name, time_diff, 'Bullish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'])
##                    elif min_var[0] == -1:                       
##                       notify(df_ticket.index[-1], name, time_diff, 'Bullish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'],  color_='STRING')
##                 if time_max < time_min:
##                    time_diff = (time_min - time_max).seconds//60
##                    max_var = get_status(df_ticket.loc[time_max]['Variação']['close'])
##                    if last_var[0] == 1:
##                       notify(df_ticket.index[-1], name, time_diff, 'Bearish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'])
##                    elif max_var[0] == 1:
##                       notify(df_ticket.index[-1], name, time_diff, 'Bearish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'], color_='STRING')

                 if time_max > time_min and not has_red:                    
                    time_diff = (time_max - time_min).seconds//60
                    if time_diff >= TIME_THRESHOLD:
                       notify(df_ticket.index[-1], name, df_ticket['Último']['close'][-1], time_diff, 'Bullish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close']) 
                 elif time_max < time_min and not has_green:
                    
                    time_diff = (time_min - time_max).seconds//60
                    if time_diff >= TIME_THRESHOLD:
                       notify(df_ticket.index[-1], name,  df_ticket['Último']['close'][-1], time_diff, 'Bearish', min/max, df_ticket['Variação']['close'][-1], df_ticket['Financeiro']['close'])  

              
                          
              if name in price_alert:
                 if isinstance(price_alert[name], float):
                    price_alert[name] = [price_alert[name]]
                 if isinstance(price_alert[name], list):
                    for i in range(len(price_alert[name])):
                       price = price_alert[name][i]
                       if df_ticket['Último']['high'][-1] >= price and df_ticket['Último']['low'][-1] <= price:              
                          notify(df_ticket.index[-1], name, df_ticket['Último']['close'][-1], time_diff, 'Alert', None, df_ticket['Variação']['close'][-1],\
                                 df_ticket['Financeiro']['close'], ignore_restrictions=True)
                          price_alert.pop(name) 
                          with open(PRICE_ALERT, 'w') as f:
                             json.dump(price_alert, f)
                          time.sleep(1)   
                          break   

def it_has(name, df_ticket, time_min, time_max):
   has_bearish = False
   has_bulish = False
   df_ticket = df_ticket[df_ticket.index >= df_ticket.index[-1] - dt.timedelta(minutes=20)]
   if len(df_ticket) == 5:
      if time_max > time_min:
         left = df_ticket[0:2]['Último']['high'].max()
         right = df_ticket[3:5]['Último']['high'].max()
         has_bearish = df_ticket['Último']['high'][2] > left and df_ticket['Último']['high'][2] > right
         if name in bull_dict and has_bearish:
            bull_dict.pop(name)
         elif name not in bull_dict and not has_bearish:                          
            bull_dict[name] = df_ticket.index[-1]

      if time_max < time_min: 
         left = df_ticket[0:2]['Último']['low'].min()
         right = df_ticket[3:5]['Último']['low'].min()
         has_bullish = df_ticket['Último']['low'][2] < left and df_ticket['Último']['low'][2] < right
         if name in bear_dict and has_bullish:
            bear_dict.pop(name)
         elif name not in bear_dict and not has_bullish:
            bear_dict[name] = df_ticket.index[-1]
   return has_bulish, has_bearish


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
   var = get_status(variation)
   if ignore_restrictions:
      print(index,'********',name, '********', price, type, variation, accum, min)
      sound_alert()
   #elif isinstance(accum, str) and 'M' in accum and 'M' in min and abs(var[1]) > 1:
   elif isinstance(accum, str) and 'M' in accum and ((var[0] == 1 and type == 'Bearish') or (var[0] == -1 and type == 'Bullish')):
      str1 =  (index,'********',name, '********', price, str(time_diff) + ' mins ', type, round(ratio,3), variation, accum, min, '\n')
      color.write(str1,'COMMENT')
      #sound_alert()
   elif isinstance(accum, str) and 'M' in accum:   
      str1 =  (index,'********',name, '********', price, str(time_diff) + ' mins ', type, round(ratio,3), variation, accum, min, '\n')
      color.write(str1,'STRING')
      #sound_alert()
    
   
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
      return row

def get_tickets():
   data = []   
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
   
   global last_date
   now = dt.datetime.today()

   df_ativo = main_df['Ativo']
   df_ativo = df_ativo.reset_index()
   df_ativo = df_ativo.set_index('Ativo')
   df_ativo = df_ativo.drop_duplicates()
   
   
   if last_date is None:
      print('Read {} tickets at {}'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S')))
   else:
      secs = (now - last_date).seconds
      if secs >= 60:
         print('Read {} tickets at {} after {} min {} secs'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S'),secs//60,secs%60))
      else:
         print('Read {} tickets at {} after {} secs'.format(len(df_ativo), dt.datetime.today().strftime('%H:%M:%S'),secs))
   last_date = dt.datetime.today()
   return main_df

def main():
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
    #insert_tickets(driver)
    while(True):

        try:
           driver.execute_script("document.getElementById('app-menu').click()")
        except:
           input('Catched Exception ...')
        driver.execute_script("document.getElementsByClassName('sector-list-table')[0].scrollTop = 0") 
        
        df = get_all_tickets_status(driver)
        
        df = df[['Ativo','Variação','Máximo','Mínimo','Data/Hora','Último', 'Abertura', 'Financeiro', 'Estado Atual']]

        df = df.drop(df[df['Ativo'] == 'IBOV'].index)

        
        df['Último'] = df['Último'].astype(float)/100        
        df['Máximo'] = df['Máximo'].astype(float)/100
        df['Mínimo'] = df['Mínimo'].astype(float)/100
        df['Abertura'] = df['Abertura'].astype(float)/100
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

def iterate():
    for index,row in main_df.iterrows():
       if row['Ativo'] == 'SOMA3':
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

