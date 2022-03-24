import tabula
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pdb
import time
import datetime as dt
import os
import pickle
import numpy as np
import DayTrade as dtr
from selenium.common.exceptions import WebDriverException
import json
import Utils as utils


PRICE_ALERT = {'MGLU3' : [23.33,22.11]}
URL = "https://rico.com.vc/arealogada/home-broker"

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
    while(True):

        
        html = get_page_source(driver)   
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 
        
        df = pd.read_html(str(tables[0]))[0]

        df = df[['Ativo','Último']]

        df['Último'] = df['Último']/100

        pdb.set_trace() 

        for key, value in d.items():
           pass
        
            
        print('Read {}, sleeping now, CTRL + C to quit...'.format(now))
        time.sleep(3)


scrap_rico()



