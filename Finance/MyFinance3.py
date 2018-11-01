import bs4 as bs
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

        
save_ibovespa_tickers()
