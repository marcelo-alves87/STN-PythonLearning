import tabula
import pandas as pd
import pdb

LEVERAGE_FILE = 'Alavancagem_Rico.txt'
MAX_LEVERAGE = 5 # 5%
BTC_FILE = 'BTC Rico 03-05-2022-9yc.pdf'

def get_leverage_tickers():
    tickers = []
    file = open(LEVERAGE_FILE, "r")
    for line in file:
        line1 = line.split('\t')
        if 'Ativo' in line1:
            pass
        else:            
            value = float(line1[1].replace(',','.'))
            if value <= MAX_LEVERAGE:
                    tickers.append([line1[0], line1[1]])    
    df = pd.DataFrame(tickers, columns=['Papel', 'Lev.'])
    return df

def get_btc_df():
    table = tabula.read_pdf(BTC_FILE, pages='all')
    df = pd.DataFrame()
    for df1 in table:
      df = df.append(df1)
    return df

def get_leverage_btc(verbose=False):
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





