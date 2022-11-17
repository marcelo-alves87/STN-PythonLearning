import pandas as pd
import pickle

df = pd.read_csv('Desagio.csv', sep=';')

def create_data(tickers):
    data = []    
    for ticker in tickers:
        try:            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            last_volume = df['Volume'][-1]
            
            if last_volume > 10**6 and last_volume < 10**9:           
                data.append(ticker)
        except:
            pass
    
    return data

tickers = []
with open("ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)        
data = create_data(tickers)

for index, row in df.iterrows():
    ticker = row['ACAO']
    desagio = float(row['DESAGIO'].replace('%',''))/100
    if desagio == 0.0075 and ticker in data:
        print(ticker)
        

