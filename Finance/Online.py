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

yfin.pdr_override()

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
EXTERNAL_JSON = "PriceServer/btc-181123_2006-181124_0105.json"

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
    global main_df, status
    if not main_df.empty:
        if os.path.exists(STATUS_FILE): 
           with open(STATUS_FILE, 'rb') as handle:
              status = pickle.load(handle)
        if os.path.exists(PRICE_ALERT):       
           with open (PRICE_ALERT, 'rb') as f:
              price_alert = json.load(f)
              
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual', 'Financeiro']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
           df_ticket = groups.loc[name][::-1]
           if name != 'IBOV' and isinstance(df_ticket, pd.Series):
              #df = update(name)
              #main_df = pd.concat([df, main_df])
              pass
           else:
              verify_alert(name, df_ticket, price_alert)
           
def verify_alert(name, df_ticket, price_alert):
   global last_ibov_var
   if isinstance(df_ticket, pd.DataFrame):
      df_ticket.set_index('Data/Hora',inplace=True)
      df_ticket.sort_index(inplace=True)

      if name == 'IBOV':
        last_ibov_var = df_ticket['Variação']['close'][-1]   
      # if name in price alert it won't be verified the ma cross.
      elif name in price_alert:
         if isinstance(price_alert[name], float):
            price_alert[name] = [price_alert[name]]
         if isinstance(price_alert[name], list):
            for i in range(len(price_alert[name])):
               price = price_alert[name][i]
               if df_ticket['Último']['high'][-1] >= price and df_ticket['Último']['low'][-1] <= price:              
                    notify(df_ticket.index[-1], name, price, 'Alert')
                    price_alert[name].remove(price) 
                    with open(PRICE_ALERT, 'w') as f:
                       json.dump(price_alert, f)
                    time.sleep(1)   
                    break   
           
      else:
         df_ticket.reset_index(inplace=True)
         myjson = { 'time' :  df_ticket['Data/Hora'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),\
                   'open' : df_ticket['Último']['open'].iloc[-1],\
                   'high' : df_ticket['Último']['high'].iloc[-1],\
                   'low' : df_ticket['Último']['low'].iloc[-1],\
                   'close' : df_ticket['Último']['close'].iloc[-1],\
                   'volume' : df_ticket['Financeiro']['close'].iloc[-1],\
                    'ativo' : name }
         with open(EXTERNAL_JSON) as json_file:
            json1 = json.load(json_file)
         df = pd.DataFrame(json1)
         df.set_index('time',inplace=True)
         df.sort_index(inplace=True)
         df.reset_index(inplace=True)
         df = df[df['ativo'] == name]
         df = df[df['time'] == myjson['time']]
         if df.empty:
            json1.append(myjson)
            with open(EXTERNAL_JSON, 'w') as f:
               json.dump(json1, f)
         else:
            index = df.index[-1]
            df = pd.DataFrame(json1)
            df.iloc[index]['high'] = myjson['high']
            df.iloc[index]['low'] = myjson['low']
            df.iloc[index]['close'] = myjson['close']
            df.iloc[index]['volume'] = myjson['volume']
            json1 = df.to_json(orient='records')            
            with open(EXTERNAL_JSON, 'w') as f:
               f.write(json1)
         time.sleep(1)
         
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
    #options_.binary_location = "C:\\Users\\55819\\Downloads\\Chrome\\chrome-win64\\chrome-win64\\chrome.exe"
    options_.add_argument("--incognito")
    options_.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(executable_path=r"Utils/chromedriver.exe")
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
   if os.path.exists('stock_dfs'):
      for file_path in os.listdir('stock_dfs'):
         name = file_path.replace('.csv','')
         df1 = pd.read_csv('stock_dfs/{}.csv'.format(name))
         df1['ativo'] = name
         df1 = df1.drop(['Unnamed: 0', 'Adj Close'], axis=1)
         df1.rename(columns={'Datetime': 'time', 'Open' : 'open', 'High' : 'high', 'Low' : 'low', 'Close' : 'close', 'Volume' : 'volume' }, inplace=True)
         df = pd.concat([df, df1])                  
   out = df.to_json(orient='records')
   with open(EXTERNAL_JSON, 'w') as f:
      f.write(out)   

def main():
    global main_df
    main_df, driver = do_scraping()
    save_csv_data()
    pdb.set_trace()
    #insert_tickets(driver)
    while(True):
        
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

        time.sleep(1)

def format_date(row):
   return row.replace('-03:00','')

def get_data_from_yahoo(ticket, actual_date):
   
   if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')
   start_date = actual_date - dt.timedelta(days=3)   
   end_date = actual_date + dt.timedelta(days=1)   
   # just in case your connection breaks, we'd like to save our progress!
   if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      try:
         ticket = format_ticket(ticket)
         print('{}'.format(ticket))
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
                      'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Adj Close'],2),\
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
   # 5 min
   # mydata = t.filter((item) => item.dtDateTime >=  new Date('2024-01-01'));

   if reset and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')      
      time.sleep(1)
      os.makedirs('stock_dfs')   
   main_df, driver = do_scraping()
   main_df = get_all_tickets_status(driver)
   tickets = main_df['Ativo'].values
   for ticket in tickets:
      if ticket != 'IBOV' and not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
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
           
            data.append({'Datetime' : date, 'Open' : n_open, 'High' : n_max, 'Low' : n_min, 'Close' : n_close, 'Adj Close' : n_close, 'Volume' : n_quantity })
         df = pd.DataFrame(data)
         df['Datetime'] = df['Datetime'] - dt.timedelta(hours = 3)
         if not os.path.exists('stock_dfs'):
            os.makedirs('stock_dfs')
         df.to_csv('stock_dfs/{}.csv'.format(ticket))           

def reset(reset_main):
   empty_json = {}
   if reset_main:
      if os.path.exists(MAIN_DF_FILE):
         os.remove(MAIN_DF_FILE)
      if os.path.exists(STATUS_FILE):   
         os.remove(STATUS_FILE)
      with open(PRICE_ALERT, 'w') as f:
         json.dump(empty_json, f)   
   
    
warnings.simplefilter(action='ignore')
reset(reset_main=True)
main()
#get_data(reset=True)


