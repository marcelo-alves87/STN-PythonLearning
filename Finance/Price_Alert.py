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

color = sys.stdout.shell
PRICE_ALERT = 'Price_Alert.txt' # write the price interval
URL = "https://rico.com.vc/arealogada/home-broker"

def notify(ticket, time1):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    path1 = 'Utils/Strike.mp3'
    utils.play('Strike',path1,'en-us')
    color.write('(' + time1 + ') ** ' + ticket + ' **\n','KEYWORD')
    
def get_page_source(driver):
   try :
       return driver.page_source       
   except WebDriverException as e:
       time.sleep(1)
       return get_page_source(driver)

def scrap_rico():

       
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL) 

    input('Wait ...')
    print('Running ...')
    while(True):

        html = get_page_source(driver)   
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 
        
        df = pd.read_html(str(tables[0]))[0]
        
        df = df[['Ativo', 'Data/Hora','Último']]

        df['Último'] = df['Último']/100
        data = {}
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
        time.sleep(3)


scrap_rico()

