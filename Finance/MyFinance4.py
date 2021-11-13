import bs4 as bs
import datetime as dt
from datetime import date, timedelta
import timedelta
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
import yfinance as yfin
import pdb

yfin.pdr_override()

def removeReference(ticker):
    index = ticker.find('[')
    if index > -1:
        ticker = ticker[:index]
    return ticker    

def formatTicker(ticker, tickers):
    ticker = ticker.rstrip()
    split = ticker.split(',')
    if len(split) > 1:
        tickers.append(removeReference(split[1].strip()))   
    tickers.append(removeReference(split[0].strip()))

def save_ibovespa_tickers():
    resp = requests.get('https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        formatTicker(ticker, tickers)
        
    with open("ibovespatickers.pickle","wb") as f:
        pickle.dump(tickers,f)


def get_data_from_yahoo(tickers = None):
    if tickers == None:      
        with open("ibovespatickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    elif isinstance(tickers, str):
        ticker = tickers
        tickers = []
        tickers.append(ticker)
        
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    tomorrow = dt.date.today() + dt.timedelta(days=1)    
    
    for ticker in tickers:
        print(ticker)
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            try:
                df = web.get_data_yahoo(ticker + '.SA', start='2021-03-01', end=tomorrow.strftime('%Y-%m-%d'))
                df.to_csv('stock_dfs/{}.csv'.format(ticker))           
            except:
                print(ticker,'não foi encontrado')
        else:
            print('Already have {}'.format(ticker))

def adjust_date(date):    
    if len(str(date)) == 7:        
        return '0' + str(date)
    else:
        return str(date)
    
def get_data_from_brinvesting(indice):

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }

    links = []
    resp = requests.get(indice, headers=headers)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'id': 'cr1'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        link = row.find('a')
        links.append('http://br.investing.com' + link['href'] + '-historical-data')
    for link in links:
        resp = requests.get(link, headers=headers)

        soup = bs.BeautifulSoup(resp.text, 'lxml')
        title = soup.title.text

        title = title.partition('(')[2]
        title = title.partition(')')[0]

        print(title)
        if not os.path.exists('stock_dfs/{}.csv'.format(title)):
            df = pd.read_html(resp.text, thousands='.', decimal=',')
            
            i = 0
            hasNotFound = True
            while hasNotFound:
                if i == len(df):
                    raise Exception('Table not found')
                else:
                    if 'Vol.' in df[i].columns and 'Último' in df[i].columns:
                        hasNotFound = False
                    else:    
                        i = i + 1
            df = df[i]
                
            df['Data'] = df['Data'].apply(lambda row: adjust_date(row))
        
            df['Date'] = pd.to_datetime(df['Data'].astype(str), format='%d%m%Y')
            df['Adj Close'] = df['Último'].astype(float)

            df['Volume'] = df['Vol.'].str.replace('M','0000')
            df['Volume'] = df['Volume'].str.replace('K','0')
            df['Volume'] = df['Volume'].str.replace(',','')
            df = df.drop('Vol.', 1)
            df = df.drop('Último', 1)
            df = df.drop('Máxima', 1)
            df = df.drop('Abertura', 1)
            df = df.drop('Var%', 1)
            df = df.drop('Data', 1)
            df = df.drop('Mínima', 1)
            df.set_index('Date', inplace=True)
            df = df.sort_values('Date')
            
            df.to_csv('stock_dfs/{}.csv'.format(title))   
        else:
            print('Already have {}'.format(title))
       
#get_data_from_yahoo()
##get_data_from_brinvesting('http://br.investing.com/indices/bovespa-components')
##get_data_from_brinvesting('https://br.investing.com/indices/small-cap-index-components')
##get_data_from_brinvesting('https://br.investing.com/indices/corporate-gov-stocks-components')
get_data_from_brinvesting('https://br.investing.com/indices/bm-fbovespa-real-estate-ifix-components')
