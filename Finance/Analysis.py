import pandas as pd
import sys
import time

PICKLE_FILE = 'btc_tickers.plk'
color = sys.stdout.shell

def calc_pct_last_diff(sma,ema):
    value = str(abs(ema[-1] - sma[-1]))
    if ema[-1] > sma[-1]:
        return color.write(value,"STRING")
    elif ema[-1] == sma[-1]:
        return color.write(value,"KEYWORD")
    else:
        return color.write(value,"COMMENT")
    
def resample(df , period):
    df_resampled = df.resample(period).last()
    
    df_resampled['EMA'] = df_resampled['Preco'].ewm(span=9, adjust=False).mean()
    df_resampled['SMA'] = df_resampled['Preco'].rolling(window=40, min_periods=0).mean()           

    return df_resampled.index[-1],df_resampled['SMA'],df_resampled['EMA']

def analysis():
    df = pd.read_pickle(PICKLE_FILE)

    grouped_df = df.groupby(["Papel"]).agg(lambda x: ','.join(x))
    data = []
    for name,group in pd.DataFrame(grouped_df).iterrows():
    
        ultimos = group['Último'].split(',')
        mins = group['Hora'].split(',')
        list_tuples = list(zip(mins, ultimos))  
        df = pd.DataFrame(list_tuples, columns=['Hora', 'Preco'])

        df['Hora'] = pd.to_datetime(df['Hora'])
        df['Preco'] = pd.to_numeric(df['Preco'])    
        df.set_index('Hora', inplace=True)

        df['EMA'] = df['Preco'].ewm(span=9, adjust=False).mean()
        df['SMA'] = df['Preco'].rolling(window=40, min_periods=0).mean()           

        sma1,ema1 = df['SMA'],df['EMA']
        time5,sma5,ema5 = resample(df,'5min')
        
    ##    calc_pct_last_diff(sma5, ema5)
    ##    calc_pct_last_diff(df['SMA'],df['EMA'])

        data.append([name,sma5,ema5,sma1,ema1])   
    print('\n')
    print(time5,df.index[-1])
    for group in data:
        color.write('\n' + group[0] + ': 5min ',"TODO") + calc_pct_last_diff(group[1],group[2]) + color.write(' , 1min ',"TODO") + calc_pct_last_diff(group[3],group[4])


while True:
    analysis()
    time.sleep(90)
