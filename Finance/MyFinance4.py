import bs4 as bs
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests

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


def get_data_from_yahoo(reload_ibovespa=False):
    if reload_ibovespa:
        tickers = save_ibovespa_tickers()
    else:
        with open("ibovespatickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2018, 11, 1)
    end = dt.datetime.now()
    for ticker in tickers:
        print(ticker)
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            try:
                df = web.DataReader(ticker + '.SA', 'yahoo', start, end)
                df.to_csv('stock_dfs/{}.csv'.format(ticker))
            except:
                print(ticker,'não foi encontrado')
        else:
            print('Already have {}'.format(ticker))


get_data_from_yahoo()
