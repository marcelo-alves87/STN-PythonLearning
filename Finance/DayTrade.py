import tabula
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pdb
import time
import datetime as dt
import os

LEVERAGE_FILE = 'Alavancagem_Rico.txt'
LEVERAGE = ['5%','10%']
BTC_FILE = 'BTC Rico.pdf'
FREE_FLOAT_FILE = 'Free-Float_9-2021.csv'
PICKLE_FILE = 'btc_tickers.plk'


def get_leverage_tickers():
    tickers = []
    file = open(LEVERAGE_FILE, "r")
    for line in file:
         line1 = line.split('\t')
         for lev in LEVERAGE:
             if lev == line1[1]:
                 tickers.append([line1[0], line1[1]])    
    df = pd.DataFrame(tickers, columns=['Papel', 'Lev.'])
    return df

def get_btc_df():
    table = tabula.read_pdf(BTC_FILE, pages='all')
    df = pd.DataFrame()
    for df1 in table:
      df = df.append(df1)
    return df

def get_leverage_btc():
    #Tickers that allow leverage
    lev_tickers = get_leverage_tickers()
    #Tickers that allow BTC
    btc_tickers = get_btc_df()

    df = pd.merge(lev_tickers, btc_tickers, on='Papel', how='outer')
    df = df[df['Disponibilidade'] == 'OK']
    df = df[df['Lev.'].notna()]
    df.drop(['Disponibilidade', 'Taxa (% a.a)'], 1, inplace=True)
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
    return df

def convert_to_float(x):    
    x = str(x)
    if len(x) == 4:
        x = x[:2] + '.' + x[-2:]
    elif len(x) == 3:
        x = x[0] + '.' + x[-2:]
    elif len(x) == 2:
        x = x[0] + '.' + x[1]
    return x

def convert_to_datetime(x):
    mytime = dt.datetime.strptime(x,'%H:%M:%S').time()
    date = dt.datetime.combine(dt.date.today(), mytime)
    return date.strftime("%Y-%m-%d %H:%M:%S")
    
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
        main_df.drop(['Lev._x', 'Nome_x'], 1, inplace=True)
        main_df.rename(columns={'Lev._y': 'Lev.', 'Nome_y': 'Nome'}, inplace=True)
        main_df.to_pickle(PICKLE_FILE)    
    return df_btc                         


def scrap_br_investing():

    df_btc = update_main_df()
        
    
    url = "https://br.investing.com/indices/bovespa-components"
    driver = webdriver.Chrome(executable_path=r"Utils/chromedriver.exe")
    driver.get(url)
    
    while(True):
        print('Reading ...')

        if os.path.isfile(PICKLE_FILE): 
            main_df = pd.read_pickle(PICKLE_FILE)
        else:
            main_df = pd.DataFrame()

        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        table = soup.find('table', id="cr1")
        
        df = pd.read_html(str(table))[0]

        df.drop(['Unnamed: 0', 'Unnamed: 9', 'Máxima', 'Mínima', 'Var.', 'Var.%'], 1, inplace=True)

        df = pd.merge(df_btc, df, left_on=df_btc["Nome"].str.lower(), right_on=df["Nome"].str.lower(), how='left')

           
        df['Hora'] = df['Hora'].apply(convert_to_datetime)
        df['Último'] = df['Último'].apply(convert_to_float)
        df.drop(['key_0', 'Nome_y'],1, inplace=True)
        df.rename(columns={'Nome_x': 'Nome'}, inplace=True)
        
        df = pd.concat([main_df, df]).reset_index(drop=True)

        df.to_pickle(PICKLE_FILE) # where to save it usually as a .plk

        print('Sleeping ...')
        time.sleep(90)


#scrap_br_investing()

