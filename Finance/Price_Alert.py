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
import datetime as dt
import pickle

color = sys.stdout.shell
MAIN_DF_FILE = 'main_df.plk'
PRICE_ALERT = 'Price_Alert.txt' # write the price interval
TREND_ALERT = 'Trend_Alert.txt' # write the price interval
URL = "https://rico.com.vc/arealogada/home-broker"
THRESHOLD = 0.015 #1.5%
b_list = []
def to_str(date):
    return date.strftime('%H:%M')

def check_leverages_tickers(df,leverage):
    df3 = df.merge(leverage, left_on=['Ativo'], right_on=['Papel'], how='outer')
    list1 = df3[df3['Ativo'].isnull()]['Papel'].to_list()
    if len(list1) > 0:
        color.write('** The following tickers arent in Rico table (' + ','.join(str(x) for x in list1) + ') **\n','COMMENT')
        
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

def notify_trend_append(ticket,time1,type1, max1, min1,data):
       notify(ticket,time1,type1)
       dict1 = {ticket: [max1,min1]}
       data.update(dict1)
       with open(TREND_ALERT, 'w') as f:
           json.dump(data, f) 
       

def notify_trend(ticket,time1,type1, max1, min1):
    if os.path.exists(TREND_ALERT):
        with open (TREND_ALERT, 'rb') as f:
            data = json.load(f)
            if ticket in data:  
                pass
            else:
                notify_trend_append(ticket,time1,type1,max1,min1,data) 
    else:
       notify_trend_append(ticket,time1,type1,max1,min1,{})
       
def notify(ticket, time1, type1='None'):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    path1 = 'Utils/Strike.mp3'
    utils.play('Strike',path1,'en-us')
    if type1 == 'None':
        color.write('(' + time1 + ') ** ' + ticket + ' **\n','KEYWORD')
    elif type1 == 'Bull':
        color.write('(' + time1 + ') ** ' + ticket + ' **\n','STRING')
    elif type1 == 'Bear':
        color.write('(' + time1 + ') ** ' + ticket + ' **\n','COMMENT')
    
def warning(ticket):
    color.write('** ' + ticket + ' ** isnt in leverage set\n','COMMENT')
    
def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def scrap_rico():
    if os.path.exists(MAIN_DF_FILE):
        main_df = pd.read_pickle(MAIN_DF_FILE)
    else:
        main_df = pd.DataFrame()
    #main_df = pd.read_pickle('df.pkl')
    if os.path.exists(TREND_ALERT):
        os.remove(TREND_ALERT)
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
            main_df.to_pickle(MAIN_DF_FILE)
        
        price_alert()
        check_leverages_tickers(main_df,leverage)
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)

        for name in groups.index.unique():
            if name == 'IBOV':
                pass
            elif not (leverage['Papel'] == name).any():
                warning(name)
                main_df = main_df.drop(main_df[main_df['Ativo'] == name].index)
            else:    
                df_ticket = groups.loc[name][::-1]
                for i in range(len(df_ticket)):
                      df_i = df_ticket.iloc[:i+1]
                      if len(df_i) > 1 and 'low' in df_i and 'high' in df_i and not isinstance(df_i['low'],float) and not isinstance(df_i['high'],float):                      
                          if df_i['low'].is_monotonic_decreasing:
                            if ((df_i.iloc[0]['close']/df_i.iloc[-1]['close']) - 1) >= THRESHOLD:
                                notify_trend(name, to_str(df_i.iloc[0]['Data/Hora']), 'Bull', df_i.iloc[0]['close'], df_i.iloc[-1]['close']) 
                          elif df_i['high'].is_monotonic_increasing:                            
                            if ((df_i.iloc[-1]['close']/df_i.iloc[0]['close']) - 1) >= THRESHOLD:
                                notify_trend(name, to_str(df_i.iloc[0]['Data/Hora']), 'Bear', df_i.iloc[-1]['close'], df_i.iloc[0]['close']) 

                               
        time.sleep(3)

scrap_rico()
#

##139082
##window.localStorage.setItem('data',JSON.stringify(t))
##then save manually to local file (TICKET.txt in stock_dfs).

##MY_TICKETS = ['ABEV3']
##
##for ticket in MY_TICKETS:
##    filepath = 'stock_dfs/' + ticket + '.txt'
##    if os.path.exists(filepath):
##           f = open(filepath)
##           data = json.load(f)
##           df = pd.json_normalize(data)
##           df['Ativo'] = ticket
##           df['Abertura'] = 0
##           df.rename(columns={'nMax': 'Máximo', 'nMin' : 'Mínimo', 'dtDateTime' : 'Data/Hora', 'nClose' : 'Último'}, inplace=True)
##           df = df[['Ativo','Máximo','Mínimo','Data/Hora','Último', 'Abertura']]
##           df['Data/Hora'] = pd.to_datetime(df['Data/Hora']) - dt.timedelta(hours=6)
##           df.set_index('Data/Hora',inplace=True)
##           f.close()



 
