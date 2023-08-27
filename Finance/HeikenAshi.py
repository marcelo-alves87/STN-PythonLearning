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
import pandas_datareader.data as web
import yfinance as yfin
import shutil

yfin.pdr_override()

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
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
status_bull = {}
status_bear = {}
score_bull = {}
score_bear = {}
MIN_SCORE = 1
EMA_DIFF = 0.01


#IMPLEMENTAR MUDANÇA DE EMA +- em diferentes dias

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

def format_ticket(ticket):
   ticket = ticket.split(' ')
   if len(ticket) == 2:
      ticket = ticket[1]
   else:
      ticket = ticket[0]
   return ticket

def format_date(row):
   return row.replace('-03:00','')

def get_data_from_yahoo(ticket, actual_date):
   
   if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')
   start_date = actual_date - dt.timedelta(days=1)   
   end_date = actual_date + dt.timedelta(days=1)   
   # just in case your connection breaks, we'd like to save our progress!
   if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      try:
         ticket = format_ticket(ticket)
         df = web.get_data_yahoo(ticket + '.SA', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="5m")
         df.reset_index(inplace=True)
         df['Datetime'] = df['Datetime'].astype(str)
         df['Datetime'] = df['Datetime'].apply(lambda row : format_date(row))
         df['Datetime'] = pd.to_datetime(df['Datetime'])
         df = df[df['Datetime'] <= actual_date]
         df.to_csv('stock_dfs/{}.csv'.format(ticket))           
      except:
         print(ticket,'not found')
   else:
      print('Already have {}'.format(ticket))


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

def to_HA(df):
    df_HA = df
    df_HA['close']=round((df['open']+ df['high']+ df['low']+df['close'])/4,2)

    #idx = df_HA.index.name
    #df_HA.reset_index(inplace=True)

    for i in range(0, len(df)):
        if i == 0:
            df_HA['open'][i]= round( ((df['open'][i] + df['close'][i] )/ 2),2)
        else:
            df_HA['open'][i] = round( ((df['open'][i-1] + df['close'][i-1] )/ 2),2)


    #if idx:
        #df_HA.set_index(idx, inplace=True)

    df_HA['high']=round(df[['open','close','high']].max(axis=1),2)
    df_HA['low']=round(df[['open','close','low']].min(axis=1),2)
    return df_HA

def which_bar(row):
   if row['high'] > row['close'] and  row['low'] < row['open'] and row['close'] > row['open']:
      return 'indecision bullish'
   elif row['high'] >= row['close'] and row['close'] > row['open']:
      return 'bullish'
   if row['low'] < row['close'] and row['high'] > row['open'] and row['close'] < row['open']:
      return 'indecision bearish'
   elif row['low'] <= row['close'] and row['close'] < row['open']:
      return 'bearish'
   else:
      return 'indecision'
   
def verify_df(name, df_ticket):
   global last_ibov_var, status_bull, status_bear, score_bull, score_bear
   if isinstance(df_ticket, pd.DataFrame):
            
        df_ticket.set_index('Data/Hora',inplace=True)
        df_ticket.sort_index(inplace=True)

        if name == 'IBOV':
                            
           last_ibov_var = df_ticket['Variação']['close'][-1]                 
        elif len(df_ticket) >= SECOND_EMA_LEN:
              
           df = to_HA(df_ticket['Último'])
           df['EMA_1'] = df['close'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
           df['EMA_2'] = df['close'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

           df = df[df.index >= df.index[-1].strftime('%Y-%m-%d 10:00:00')]

           if not df.empty:
   
              diff = round(abs(df['EMA_2'][-1] - df['EMA_1'][-1]),3)

              bar = which_bar(df.iloc[-1])

              if df['EMA_1'][-1] >= df['EMA_2'][-1]:
                 if name not in status_bear:
                    status_bear[name] = []
                 if name in status_bull and (bar == 'bearish' or bar == 'indecision bearish') and diff >= EMA_DIFF:
                    if df.index[-1] not in status_bull[name]:
                       status_bull[name].append(df.index[-1])
                    
                 
              elif df['EMA_1'][-1] < df['EMA_2'][-1]:
                  if name not in status_bull:
                    status_bull[name] = []
                  if name in status_bear and (bar == 'bullish' or bar == 'indecision bullish') and diff >= EMA_DIFF:
                     if df.index[-1] not in status_bear[name]:
                       status_bear[name].append(df.index[-1])
                   
                 
              if name in status_bull and len(status_bull[name]) >= MIN_SCORE and name not in score_bull:
                 score_bull[name] = len(status_bull[name])
                 print(name, 'Bull', df.index[-1], len(status_bull[name]), diff)
              #elif name in status_bull and len(status_bull[name]) >= MIN_SCORE and score_bull[name] < len(status_bull[name]):
              #   score_bull[name] = len(status_bull[name])
              #   print(name, 'Bull', df.index[-1], len(status_bull[name]), diff)
              elif name in status_bear and len(status_bear[name]) >= MIN_SCORE and name not in score_bear:
                 score_bear[name] = len(status_bear[name])
                 print(name, 'Bear', df.index[-1], len(status_bear[name]), diff)
              #elif name in status_bear and len(status_bear[name]) >= MIN_SCORE and score_bear[name] < len(status_bear[name]):
              #   score_bear[name] = len(status_bear[name])
              #    print(name, 'Bear', df.index[-1], len(status_bear[name]), diff) 
              
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
            if update_tickets:
               df = update(df)
                  
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

def update(df):
   data = []
   df3 = df['Ativo'].drop_duplicates()
   for i in range(len(df3)):
      ticket = format_ticket(df3[i])
      get_data_from_yahoo(ticket, df[df['Ativo'] == df3[i]].index[0])      
      if os.path.exists('stock_dfs/{}.csv'.format(ticket)):
         df4 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
         for index,row in df4.iterrows():
            date = dt.datetime.strptime(row['Datetime'], '%Y-%m-%d %H:%M:%S')
            _data = {'Data/Hora' : date.strftime('%Y-%m-%d %H:%M:%S'), 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Adj Close'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'}
            data.append(_data)
            data.append({'Data/Hora' : (date - dt.timedelta(minutes = 1)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Low'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
            data.append({'Data/Hora' : (date - dt.timedelta(minutes = 2)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['High'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
            data.append({'Data/Hora' : (date - dt.timedelta(minutes = 3)).strftime('%Y-%m-%d %H:%M:%S') , 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Open'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : 0, 'Estado Atual' : 'Aberto'})
   df4 =  pd.DataFrame(data)
   df4['Data/Hora'] = pd.to_datetime(df4['Data/Hora'])
   df4.set_index('Data/Hora', inplace=True)
   df4.sort_index(inplace=True)
   df4 = df4[df4.index > df4.index[0].strftime('%Y-%m-%d 10:00:00')]
   df3 = df4[df4.index < df4.index[0].strftime('%Y-%m-%d 18:00:00')]
   df5 = df4[df4.index > df4.index[-1].strftime('%Y-%m-%d 10:00:00')]
   df = pd.concat([df3, df5, df])
   return df

def iterate(ticket):
    main_df = pd.read_pickle(MAIN_DF_FILE)
    for index,row in main_df.iterrows():
       if row['Ativo'] == ticket:
          print(index,row['Último'],row['Variação'])

def test(update_tickets):
    global status_bull, status_bear, score_bull, score_bear
    if not os.path.exists(MAIN_DF_FILE):
       date1 = '2023-08-25'
       tickets = get_tickets()
       df1 = pd.DataFrame({'Ativo' : tickets, 'Data/Hora' : dt.datetime.strptime(date1 + ' 18:00:00', '%Y-%m-%d %H:%M:%S')})
       df1.set_index('Data/Hora', inplace=True)
       df1 = update(df1)
       df1 = df1[df1.index > date1]
       df1.dropna(inplace=True)
       df1.to_pickle(MAIN_DF_FILE, protocol=2)       
    main_df = pd.read_pickle(MAIN_DF_FILE)
    time1 =  main_df.index[0]    
    last_time = main_df.index[-1]
    if update_tickets:
       main_df = update(main_df)
    
    while time1 < last_time:
        df = main_df.reset_index()
        df = df[df['Data/Hora'] <= time1]        
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row)) 
        df['Financeiro'] = df['Financeiro'].astype(float)
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)
         
        verify_trends(df)

        #time.sleep(1)
        time1 += dt.timedelta(minutes = 5)

        if time1.strftime('%H:%M') == '17:00':
           print('changing day')
           status_bull = {}
           status_bear = {}
           score_bull = {}
           score_bear = {} 
           time1 -= dt.timedelta(hours = 7)
           time1 += dt.timedelta(days = 1)
           
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
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')
   with open(PRICE_ALERT, 'w') as f:
      json.dump(empty_json, f)
   
      
warnings.simplefilter(action='ignore')
#reset(reset_main=True)
#main(update_tickets=True)
test(update_tickets=True)
#iterate('PETZ3')
#get_data('PETZ3')
#test_ticket('PETZ3')
