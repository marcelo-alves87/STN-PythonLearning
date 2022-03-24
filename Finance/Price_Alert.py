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

PRICE_ALERT = 'Price_Alert.txt' # please write the price interval
URL = "https://rico.com.vc/arealogada/home-broker"

def notify(ticket):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    path1 = 'Utils/Strike.mp3'
    utils.play('Strike',path1,'en-us')

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

        df = df[['Ativo','Último']]

        df['Último'] = df['Último']/100
        data = {}
        if os.path.exists(PRICE_ALERT):
           with open(PRICE_ALERT) as f:
             data = json.load(f)
           for ticket, interval in list(data.items()):
              df2 = df[df['Ativo'] == ticket]
              if not df2.empty:
                 value = df2.iloc[-1]['Último']
                 if value >= interval[0] or value <= interval[1]:
                    notify(ticket)
                    data.pop(ticket, None)
                    with open(PRICE_ALERT, 'w') as f:
                       json.dump(data, f)                  
        time.sleep(3)


scrap_rico()

