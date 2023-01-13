import tabula
import pandas as pd
import pdb
import pickle

BTC_FILE = 'BTC Rico 13-01-2023--k0.pdf'

def get_btc_df():
    table = tabula.read_pdf(BTC_FILE, pages='all')
    df = pd.DataFrame()
    for df1 in table:
      df = df.append(df1)
    return df


def handle_taxa(row):
    row = float(row.replace(',','.'))
    return row

with open("Old_Finance/ibovespatickers.pickle", "rb") as f:
    tickers = pickle.load(f)



df_btc = get_btc_df()
df_btc['Taxa (% a.a)'] = df_btc['Taxa (% a.a)'].apply(lambda row: handle_taxa(row))
df_btc = df_btc[df_btc['Taxa (% a.a)'] < 1]


for ticker in tickers:
    df = pd.read_csv('Old_Finance/stock_dfs/{}.csv'.format(ticker))
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    if len(df.index) > 2 and df['Volume'][-2] >= 10**7 and df['Volume'][-2] < 10**8 and (df_btc['Papel'] == ticker).any():
        print(ticker, str(df_btc.loc[df_btc['Papel'] == ticker]['Taxa (% a.a)'].values[0]) + '%',\
              str(df_btc.loc[df_btc['Papel'] == ticker]['Disponibilidade'].values[0]))
