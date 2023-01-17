import tabula
import pandas as pd
import pdb
import pickle
import os

BTC_FILE = 'BTC Rico 13-01-2023--k0.pdf'

def get_btc_df():
    table = tabula.read_pdf(BTC_FILE, pages='all')
    df = pd.DataFrame()
    for df1 in table:
      df = df.append(df1)

    df['Taxa (% a.a)'] = df['Taxa (% a.a)'].apply(lambda row: handle_taxa(row))
    #df = df[df['Taxa (% a.a)'] < 10]
  
    return df


def handle_taxa(row):
    row = float(row.replace(',','.'))
    return row

def handle_volume(volume):
    if volume > 10**9:
        return str(round(volume/10**9,2)) + 'B'
    elif volume > 10**6:
        return str(round(volume/10**6,2)) + 'M'
    elif volume > 10**3:
        return str(round(volume/10**3,2)) + 'k'
    else:
        return volume
    
def btc_volume(tickers=None):

    df_btc = get_btc_df()

    if tickers == None:     
        with open("Old_Finance/ibovespatickers.pickle", "rb") as f:
            tickers = pickle.load(f)

    for ticker in tickers:
        if os.path.exists('Old_Finance/stock_dfs/{}.csv'.format(ticker)):
            df = pd.read_csv('Old_Finance/stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            #if len(df.index) > 2:
            if len(df.index) > 2 and df['Volume'][-2] >= 10**6 and (df_btc['Papel'] == ticker).any():
                print(ticker)
                #print(ticker, str(df_btc.loc[df_btc['Papel'] == ticker]['Taxa (% a.a)'].values[0]) + '%',\
                #      str(df_btc.loc[df_btc['Papel'] == ticker]['Disponibilidade'].values[0]), handle_volume(df['Volume'][-2]))
        else:
            print('%s not found!' %ticker)

def ticker_details():
    tickers = []
    f = open("Tickets.txt", "r")
    for line in f:        
        tickers.append(line.rstrip())

    btc_volume(tickers)
        
btc_volume()
