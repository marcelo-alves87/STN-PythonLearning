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


MAIN_DF_FILE = 'main_df_03022023.pickle'
URL = "https://rico.com.vc/"
count_ticket_short = {}
count_ticket_long = {}
last_lvl = {}

def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def verify_trends(main_df):
    global last_lvl
    global count_ticket_short
    global count_ticket_long
    
    if not main_df.empty:
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
         df_ticket = groups.loc[name][::-1]
         
         
         if isinstance(df_ticket, pd.DataFrame) and len(df_ticket.index) > 2:
           df_ticket.set_index('Data/Hora',inplace=True)
           df_ticket.sort_index(inplace=True)
           if name not in last_lvl and df_ticket['Mínimo']['open'][-1] > df_ticket['Mínimo']['low'][-1] \
              and df_ticket['Mínimo']['open'][-1]/df_ticket['Máximo']['close'][-1] < 0.98:
              do_count_ticket(name, count_ticket_short)
              last_lvl[name] = df_ticket['Mínimo']['open'][-1]
              notify(df_ticket.index[-1], name, 'Short', df_ticket['Máximo']['close'][-1], df_ticket['Mínimo']['open'][-1], count_ticket_short[name])
           elif name in last_lvl and df_ticket['Último']['low'][-1] > last_lvl[name]:
              last_lvl.pop(name)

           if name not in last_lvl and df_ticket['Máximo']['open'][-1] < df_ticket['Máximo']['high'][-1] \
              and df_ticket['Mínimo']['close'][-1]/df_ticket['Máximo']['open'][-1] < 0.98:
              do_count_ticket(name, count_ticket_long)
              last_lvl[name] = df_ticket['Máximo']['open'][-1]
              notify(df_ticket.index[-1], name, 'Long', df_ticket['Máximo']['open'][-1], df_ticket['Mínimo']['close'][-1], count_ticket_long[name])
           elif name in last_lvl and df_ticket['Último']['high'][-1] < last_lvl[name]:
              last_lvl.pop(name)   

def do_count_ticket(name, count_ticket):
   
   if name not in count_ticket:
      count_ticket[name] = 1
   else:
      count_ticket[name] += 1

def notify(index, name, type, lvl0, lvl100, count):
   print(index,'********',name, '********', type, lvl0, lvl100, round(lvl100/lvl0,3), count)
   #winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   #time.sleep(1)

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
              
def main():
    main_df = pd.DataFrame()
    if os.path.exists(MAIN_DF_FILE):
        main_df = pd.read_pickle(MAIN_DF_FILE)    
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Waiting ...')
    driver.switch_to.window(driver.window_handles[1])
    print('Running ...')
    #insert_tickets(driver)
    while(True):

        
        driver.execute_script("document.getElementById('app-menu').click()")

        
        
        html = get_page_source(driver)   
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 

        df = pd.read_html(str(tables[0]))[0]

        df = df[['Ativo','Máximo','Mínimo','Data/Hora','Último', 'Abertura', 'Financeiro']]

        df = df.drop(df[df['Ativo'] == 'IBOV'].index)        
          
        df['Último'] = df['Último']/100
        df['Máximo'] = df['Máximo']/100
        df['Mínimo'] = df['Mínimo']/100
        df['Abertura'] = df['Abertura']/100
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row))  

        df['Data/Hora'] = df['Data/Hora'].replace('-','00:00:00') 
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])

        start_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 10:00:00'
        end_date = dt.datetime.today().strftime('%Y-%m-%d') + ' 18:00:00'

        df = df[df['Data/Hora'] >= start_date]
        df = df[df['Data/Hora'] <= end_date]
        
        df.set_index('Data/Hora',inplace=True)

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
        
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)

        
        verify_trends(df)

        #time.sleep(1)
        time1 += dt.timedelta(minutes = 5)

    

def reset(reset_main):
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   
  
reset(reset_main=False)
#main()
test()

