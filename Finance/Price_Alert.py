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
THRESHOLD = 0.01 #1%
MY_TARGETS = [0.00, -0.272, -0.618, -1.618]
b_list = ['IBOV']
def to_str(date):
    return date.strftime('%H:%M')

def check_leverages_tickers(df,leverage):
    df3 = df.merge(leverage, left_on=['Ativo'], right_on=['Papel'], how='outer')
    list1 = df3[df3['Ativo'].isnull()]['Papel'].to_list()
    if len(list1) > 0:
        color.write('** The following tickers arent in Rico table (' + ','.join(str(x) for x in list1) + ') **\n','COMMENT')
        
def price_alert(df):
    if os.path.exists(PRICE_ALERT):
       with open(PRICE_ALERT) as f:
         data = json.load(f)
       for ticket, interval in list(data.items()):
          df2 = df[df['Ativo'] == ticket]
          if not df2.empty:
             df2.reset_index(inplace=True) 
             value = df2.iloc[-1]['Último']
             time1 = df2.iloc[-1]['Data/Hora']
             if value >= interval[0] or value <= interval[1]:
                warning(ticket,time1) 
                notify(ticket)
                data.pop(ticket, None)
                with open(PRICE_ALERT, 'w') as f:
                   json.dump(data, f) 

def warning_trend_append(ticket,time1,type1, max1, min1,trends):
       warning(ticket,time1,type1)
       dict1 = {ticket: { 'Prices' : [max1,min1], 'Type' : type1 }}
       trends.update(dict1)
       with open(TREND_ALERT, 'w') as f:
           json.dump(trends, f) 

def warning(ticket,time1,type1=None,targets=None):
    if type1 is None:
        color.write('(' + to_str(time1) + ') ** ' + ticket + ' **\n','KEYWORD')
    elif type1 == 'Bull':
        color.write('(' + to_str(time1) + ') ** ' + ticket + ' **\n','STRING')
    elif type1 == 'Bear':
        color.write('(' + to_str(time1) + ') ** ' + ticket + ' **\n','COMMENT')
    if targets is not None:
        for i,j in enumerate(targets):
            color.write(ticket + ' ( Target ' + str(i+1) + '): ' + str(j) + '\n','KEYWORD')
            
def notify(ticket):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    path1 = 'Utils/Strike.mp3'
    utils.play('Strike',path1,'en-us')
    
    
def warning_(ticket):
    color.write('** ' + ticket + ' ** isnt in leverage set\n','COMMENT')

def update_trend(name,dict1,trends):
    del trends[name]                    
    trends.update(dict1)
    with open(TREND_ALERT, 'w') as f:
        json.dump(trends, f)

def remove_trend(name,trends):
    del trends[name]     
    with open(TREND_ALERT, 'w') as f:
        json.dump(trends, f)
        
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
##    if os.path.exists(TREND_ALERT):
##        os.remove(TREND_ALERT)
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
        
        price_alert(main_df)
        check_leverages_tickers(main_df,leverage)
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        trends = {}
        if os.path.exists(TREND_ALERT):
            with open (TREND_ALERT, 'rb') as f:
                trends = json.load(f)
                
        
        for name in groups.index.unique():
            if name in b_list:
                pass
            elif not (leverage['Papel'] == name).any():
                warning_(name)
                main_df = main_df.drop(main_df[main_df['Ativo'] == name].index)
            elif name in trends:
                df_ticket = groups.loc[name]
                df_i = df_ticket.iloc[-1]

                if trends[name]['Type'] == 'Bull' and df_i['high'] > trends[name]['Prices'][0]:
                    trends[name]['Prices'][0] = df_i['high']
                    dict1 = {name : trends[name]}
                    update_trend(name,dict1,trends)
                elif trends[name]['Type'] == 'Bear' and df_i['low'] < trends[name]['Prices'][1]:
                    trends[name]['Prices'][1] = df_i['low']
                    dict1 = {name : trends[name]}
                    update_trend(name,dict1,trends)
                elif trends[name]['Type'] == 'Bull':
                     length = trends[name]['Prices'][0] - trends[name]['Prices'][1]
                     fib618 = trends[name]['Prices'][0] - length*0.618
                     fib50 = trends[name]['Prices'][0] - length*0.5
                     fib382 = trends[name]['Prices'][0] - length*0.382

                     if df_i['close'] < fib382 and df_i['close'] > fib618:
                         notify(name)
                         targets = []
                         for i in MY_TARGETS:
                             targets.append(trends[name]['Prices'][0] - length*i)
                         warning(name,df_i['Data/Hora'],'Bull',targets)
                         remove_trend(name,trends)
                        
                elif trends[name]['Type'] == 'Bear':
                     length = trends[name]['Prices'][0] - trends[name]['Prices'][1]
                     fib618 = trends[name]['Prices'][1] + length*0.618
                     fib50 = trends[name]['Prices'][1] + length*0.5
                     fib382 = trends[name]['Prices'][1] + length*0.382

                     if df_i['close'] > fib382 and df_i['close'] < fib618:
                         notify(name)
                         targets = []
                         for i in MY_TARGETS:
                             targets.append(trends[name]['Prices'][1] + length*i)
                         warning(name,df_i['Data/Hora'],'Bear',targets)
                         remove_trend(name,trends)
                         
            else:    
                df_ticket = groups.loc[name][::-1]
                for i in range(len(df_ticket)):
                      df_i = df_ticket.iloc[:i+1]
                      if len(df_i) > 1 and 'low' in df_i and 'high' in df_i and not isinstance(df_i['low'],float) and not isinstance(df_i['high'],float):                      
                          if df_i['low'].is_monotonic_decreasing:
                            if ((df_i.iloc[0]['high']/df_i.iloc[-1]['low']) - 1) >= THRESHOLD:
                                warning_trend_append(name, df_i.iloc[0]['Data/Hora'], 'Bull', df_i.iloc[0]['high'], df_i.iloc[-1]['low'],trends)
                                break
                          elif df_i['high'].is_monotonic_increasing:                            
                            if ((df_i.iloc[-1]['high']/df_i.iloc[0]['low']) - 1) >= THRESHOLD:
                                warning_trend_append(name, df_i.iloc[0]['Data/Hora'], 'Bear', df_i.iloc[-1]['high'], df_i.iloc[0]['low'],trends)
                                break

                               
        time.sleep(3)

scrap_rico()
#pdb.set_trace()        
#
## how to scrap rico data
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



 
