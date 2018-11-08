from collections import Counter
import numpy as np
import pandas as pd

def process_data_for_labels(ticker):
    hm_days = 7
    df = pd.read_csv('ibovespa_joined_closes.csv', index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)
    #print(df['{}'.format(ticker)])
    for i in range(1, hm_days+1):
        df['{}_{}d'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]
        #print(df['{}_{}d'.format(ticker, i)])
    df.fillna(0, inplace=True)
    return tickers, df


def buy_sell_hold(*args):
    cols = [c for c in args]
    #Se variar em torno de 2% em 1 até 7 dias
    #O suporte é hold
    #A resistência de 2% é buy
    #Se ultrapassar o suporte em -2% é sell
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0

def extract_featuresets(ticker):
    #Retorna todos os tickers
    #Retorna a variação do percentual de 1 a 7 dias do ticker
    tickers, df = process_data_for_labels(ticker)

    #Faz o buy sell ou hold com base na listagem do percentual do ticker
    df['{}_target'.format(ticker)] = list(map( buy_sell_hold,
                                               df['{}_1d'.format(ticker)],
                                               df['{}_2d'.format(ticker)],
                                               df['{}_3d'.format(ticker)],
                                               df['{}_4d'.format(ticker)],
                                               df['{}_5d'.format(ticker)],
                                               df['{}_6d'.format(ticker)],
                                               df['{}_7d'.format(ticker)] ))
    
    #Informa qual o balanceamento das classes buy sell e hold nos dados
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('{} data spread:'.format(ticker),Counter(str_vals))

    #Configura o frame    
    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    #Faz a variação de 1 dia de todos os tickers
    df_vals = df[[ticker for ticker in tickers]].pct_change()

    #Configura o frame
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    #A correlação vai ser medida
    X = df_vals.values
    y = df['{}_target'.format(ticker)].values

    return X,y,df

extract_featuresets('ABEV3')
