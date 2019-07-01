#import bs4 as bs
import pickle
#import requests
import pandas as pd

##def removeReference(ticker):
##    index = ticker.find('[')
##    if index > -1:
##        ticker = ticker[:index]
##    return ticker    
##
##def formatTicker(ticker, tickers):
##    ticker = ticker.rstrip()
##    split = ticker.split(',')
##    if len(split) > 1:
##        tickers.append(removeReference(split[1].strip()))   
##    tickers.append(removeReference(split[0].strip()))

##def save_ibovespa_tickers():
##    resp = requests.get('https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa')
##    soup = bs.BeautifulSoup(resp.text, 'lxml')
##    table = soup.find('table', {'class': 'wikitable sortable'})
##    tickers = []
##    for row in table.findAll('tr')[1:]:
##        ticker = row.findAll('td')[0].text
##        formatTicker(ticker, tickers)
##        
##    with open("ibovespatickers.pickle","wb") as f:
##        pickle.dump(tickers,f)


##def save_ibovespa_tickers():
##    resp = requests.get('https://br.advfn.com/indice/ibovespa')
##    soup = bs.BeautifulSoup(resp.text, 'lxml')
##    tds = soup.findAll('td', {'class': 'String Column2'})
##    tickers = []
##    for row in tds:
##        tickers.append(row.text.strip())
##
##    with open("ibovespatickers.pickle","wb") as f:
##        pickle.dump(tickers,f)

#Data from http://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/ibovespa.htm
#Updated in 17/1/2019
def save_ibovespa_tickers():
    tickers = []
    df = pd.read_excel('FREE-FLOAT.xlsx', sheet_name='FreeFloat')
    for i in df['Código']:
        if type(i) is str:
            print(i)
            tickers.append(i)
    
    with open("ibovespatickers.pickle","wb") as f:
        pickle.dump(tickers,f)

save_ibovespa_tickers()
