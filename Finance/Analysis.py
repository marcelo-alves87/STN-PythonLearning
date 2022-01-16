import pandas as pd

PICKLE_FILE = 'btc_tickers.plk'

def calc_pct_diff_last(df1,df2):
    x = df1[-1]
    y = df2[-1]
    return round(1 - (x/y),2)


df = pd.read_pickle(PICKLE_FILE)
grouped_df = df.groupby(["Papel"]).agg(lambda x: ','.join(x))
for name,group in pd.DataFrame(grouped_df).iterrows():
    #print(name)
    ultimos = group['Último'].split(',')
    mins = group['Hora'].split(',')
    list_tuples = list(zip(mins, ultimos))  
    df = pd.DataFrame(list_tuples, columns=['Hora', 'Preco'])

    df['Hora'] = pd.to_datetime(df['Hora'])
    df['Preco'] = pd.to_numeric(df['Preco'])    
    df.set_index('Hora', inplace=True)

    df['EMA'] = df['Preco'].ewm(span=9, adjust=False).mean()
    df['SMA'] = df['Preco'].rolling(window=40, min_periods=0).mean()           

    df_resampled = df.resample('5min').last()
    
    df_resampled['EMA'] = df_resampled['Preco'].ewm(span=9, adjust=False).mean()
    df_resampled['SMA'] = df_resampled['Preco'].rolling(window=40, min_periods=0).mean()           
    print('Ação {}: 5 min -> {}, 1 min -> {}'.format(name,calc_pct_diff_last(df['SMA'], df['EMA']),calc_pct_diff_last(df_resampled['SMA'],df_resampled['EMA'])))

