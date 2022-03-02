import tabula
import pandas as pd


LEVERAGE_FILE = 'Alavancagem_Rico.txt'
LEVERAGE = [5,6] #5% to 6%
FREE_FLOAT_FILE = 'Free-Float_1-2022.csv'
BTC_FILE = 'BTC Rico 23-02-2022-aEM.pdf'

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




