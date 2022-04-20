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

color = sys.stdout.shell
PRICE_ALERT = 'Price_Alert.txt' # write the price interval
URL = "https://rico.com.vc/arealogada/home-broker"
b_list = []
THRESHOLD = 0.2 #20 centavos

def price_alert():
    if os.path.exists(PRICE_ALERT):
       with open(PRICE_ALERT) as f:
         data = json.load(f)
       for ticket, interval in list(data.items()):
          df2 = df[df['Ativo'] == ticket]
          if not df2.empty:
             value = df2.iloc[-1]['Último']
             time1 = df2.iloc[-1]['Data/Hora']
             if value >= interval[0] or value <= interval[1]:
                notify(ticket,time1)
                data.pop(ticket, None)
                with open(PRICE_ALERT, 'w') as f:
                   json.dump(data, f) 

def notify(ticket, time1):
    global b_list
    if ticket not in b_list:
        path1 = 'Utils/' + ticket + '.mp3'    
        utils.play(ticket,path1,'pt-br')
        path1 = 'Utils/Strike.mp3'
        utils.play('Strike',path1,'en-us')
        color.write('(' + time1 + ') ** ' + ticket + ' **\n','KEYWORD')
        b_list.append(ticket)

def warning(ticket):
    color.write('** ' + ticket + ' ** not in leverage set\n','COMMENT')
    
def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def scrap_rico():
    main_df = pd.DataFrame()
    leverage = dtr.get_leverage_btc(True)  
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Wait ...')
    driver.switch_to.window(driver.window_handles[1])
    print('Running ...')
    while(True):
        
        
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
        df.set_index('Data/Hora',inplace=True)
        
        if main_df.empty:
            main_df = df
        else:
            main_df = pd.concat([main_df, df])

        price_alert()
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        
        for name in groups.index.unique():
            df_ticket = groups.loc[name][::-1]
            for i in range(len(df_ticket)):
                if (df_ticket[:i+1]['low'].is_monotonic_decreasing or df_ticket[:i+1]['high'].is_monotonic_increasing):
                    pdb.set_trace()
                    if abs(df_ticket[:i+1].iloc[-1]['close'] - df_ticket[:i+1].iloc[0]['close']) >= THRESHOLD:
                        notify(name, df_ticket.iloc[0]['Data/Hora']) 
                        break
        time.sleep(3)


scrap_rico()
 
##        global b_list
##        for index, row in df.iterrows():
##            if row['Ativo'] != 'IBOV' and row['Ativo'] not in b_list:
##                
##                length = row['Máximo'] - row['Mínimo']
##
##                if length >= 0.35:
##                
##                    if row['Último'] > row['Abertura']:                   
##
##                        fib618 = row['Máximo'] - length*0.618
##
##                        fib50 = row['Máximo'] - length*0.5
##
##                        fib382 = row['Máximo'] - length*0.382
##
##                        if row['Último'] < fib382 and row['Último'] > fib618:
##                            notify(row['Ativo'],row['Data/Hora'])
##                            print('Fibonacci Levels:\n')
##                            for i,j in enumerate([0.00, -0.272, -0.618, -1.618]):
##                                print('Level {} : {}'.format(i,row['Máximo'] - length*j))
##
##                    else:
##
##                        fib618 = row['Mínimo'] + length*0.618
##
##                        fib50 = row['Mínimo'] + length*0.5
##
##                        fib382 = row['Mínimo'] + length*0.382
##
##                        if row['Último'] > fib382 and row['Último'] < fib618:
##                            notify(row['Ativo'],row['Data/Hora'])
##                            print('Fibonacci Levels:\n')
##                            for i,j in enumerate([0.00, -0.272, -0.618, -1.618]):
##                                print('Level {} : {}'.format(i,row['Mínimo'] + length*j))

