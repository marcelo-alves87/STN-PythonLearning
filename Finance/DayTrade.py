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


LEVERAGE_FILE = 'Alavancagem_Rico.txt'
LEVERAGE = [5,6] #5% to 6%
BTC_FILE = 'BTC Rico 15-02-2022-0CA.pdf'
FREE_FLOAT_FILE = 'Free-Float_1-2022.csv'
PICKLE_FILE = 'btc_tickers.plk'
URL = "https://rico.com.vc/arealogada/home-broker"

def get_leverage_tickers():
    tickers = []
    file = open(LEVERAGE_FILE, "r")
    for line in file:        
        line1 = line.split('\t')
        for lev in range(LEVERAGE[0],LEVERAGE[1]):
            lev1 = "{:.0%}".format(lev * 0.01)                     
            if lev1 == line1[1]:
                tickers.append([line1[0], line1[1]])    
    df = pd.DataFrame(tickers, columns=['Papel', 'Lev.'])
    return df

def get_btc_df():
    table = tabula.read_pdf(BTC_FILE, pages='all')
    df = pd.DataFrame()
    for df1 in table:
      df = df.append(df1)
    return df

def get_leverage_btc(verbose=True):
    #Tickers that allow leverage
    lev_tickers = get_leverage_tickers()
    #Tickers that allow BTC
    btc_tickers = get_btc_df()

    df = pd.merge(lev_tickers, btc_tickers, on='Papel', how='outer')
    df = df[df['Disponibilidade'] == 'OK']
    df = df[df['Lev.'].notna()]
    df.drop(['Disponibilidade', 'Taxa (% a.a)'], 1, inplace=True)

    if verbose:
        print(df)
    return df

def get_free_float():
    df = pd.read_csv(FREE_FLOAT_FILE, sep=';')
    data = []
    for i,item in df['Tipo'].iteritems():
         items = item.split(' ')
         if len(items) > 1:
             data.append(df['Acao'][i] + ' ' + items[0])
         else:
             data.append(df['Acao'][i])
    df['Nome'] = data
    df['Nome'] = df['Nome'].str.replace('S/A','')
    df['Nome'] = df['Nome'].str.strip()
    df.rename(columns={'Codigo': 'Papel'}, inplace=True)
    df.replace('SID NACIONAL', 'CSN ON', inplace=True)
    df.replace('GERDAU MET PN', 'MET. GERDAU PN', inplace=True)
    df.replace('ITAUUNIBANCO PN', 'ITAU UNIBANCO PN', inplace=True)
    df.replace('MAGAZ LUIZA ON', 'MAGAZINE LUIZA ON', inplace=True)
    df.replace('ENERGIAS BR', 'EDP BRASIL ON', inplace=True)	 
    return df


def convert_to_datetime_str(x):
   try:
       mytime = dt.datetime.strptime(x,'%H:%M:%S').time()
       date = dt.datetime.combine(dt.date.today(), mytime)
       return date.strftime("%Y-%m-%d %H:%M:%S")
   except:
       return np.NaN
        
def merge_free_float_with_btc():
    #Tickers that allow leverage and BTC
    df1 = get_leverage_btc()
    df2 = get_free_float()
    df = pd.merge(df1, df2, on='Papel', how='outer')
    df.drop(['Acao', 'Tipo', 'Free Float'], 1, inplace=True)
    df = df[df['Lev.'].notna()]
    return df

def update_main_df():
    
    df_btc = merge_free_float_with_btc()
    if os.path.isfile(PICKLE_FILE):
        main_df = pd.read_pickle(PICKLE_FILE)
        main_df = pd.merge(main_df, df_btc, on='Papel', how='outer')
        main_df.drop(['Lev._x', 'Nome'], 1, inplace=True)
        main_df.rename(columns={'Lev._y': 'Lev.'}, inplace=True)
        main_df.to_pickle(PICKLE_FILE)    
    return df_btc                         


def scrap_rico():

    df_btc = update_main_df()
        
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe",options=options)
    driver.get(URL)

    input('Ready?')
    
    while(True):
        
        print('Reading, do not close ...')

        if os.path.isfile(PICKLE_FILE): 
            main_df = pd.read_pickle(PICKLE_FILE)
        else:
            main_df = pd.DataFrame()

        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')

        tables = soup.find_all('table', class_='nelo-table-group') 

        df = pd.read_html(str(tables[0]))[0]
        
        df = df[['Ativo','Último', 'Data/Hora', 'Financeiro', 'Mínimo', 'Máximo']]

        df['Último'] = df['Último']/100
        df['Máximo'] = df['Máximo']/100
        df['Mínimo'] = df['Mínimo']/100
        
        df = pd.merge(df_btc, df, left_on=df_btc["Papel"], right_on=df["Ativo"], how='left')
        df = df[['Papel', 'Lev.', 'Último', 'Data/Hora', 'Financeiro', 'Mínimo', 'Máximo']]
        df = df.dropna()
        df.rename(columns={'Data/Hora': 'Hora', 'Financeiro': 'Volume'}, inplace=True)
           
        now = df['Hora'].iloc[-1]
        
        df['Hora'] = df['Hora'].apply(convert_to_datetime_str)
        df = df.dropna()
        if len(df) > 0:
            df = pd.concat([main_df, df]).reset_index(drop=True)
            df.to_pickle(PICKLE_FILE) # where to save it usually as a .plk
            
        print('Read {}, sleeping now, CTRL + C to quit...'.format(now))
        time.sleep(5)


scrap_rico()

