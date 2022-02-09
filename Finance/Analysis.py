import pandas as pd
import os
import pdb
import sys
import time
import datetime as dt

PICKLE_FILE = 'btc_tickers.plk'
DATA_FILE = 'btc_data.plk'
color = sys.stdout.shell
windows = [5,8,13]
windows_color = ['DEFINITION', 'KEYWORD', 'COMMENT']
period = '5min'

def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)

def convert_to_datetime(x):
    
    if x != x: #is nan
        return ''
    elif x == '':
        return ''
    else:
        
        date = dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')           
        
        return date

def get_last_data():
    if os.path.exists(DATA_FILE):
         with open(DATA_FILE,"rb") as f:
            return pickle.load(f)
    else:
        return []
    
def reset_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def try_to_get_df():
    try:
        df = pd.read_pickle(PICKLE_FILE)
        return df
    except:
        return None

def create_resampled_from_group(group):
    list1 = group[1]['Hora'].split(';')
    list2 = group[1]['Último'].split(';')
    df = pd.DataFrame({'Hora' : list1, 'Último' : list2})
    df['Hora'] = df['Hora'].apply(convert_to_datetime)
    df['Último'] = df['Último'].apply(convert_to_float)
    df.set_index('Hora', inplace=True)
        
    if not df.empty:        
        df_resampled = df.resample(period).last()
        df_resampled = df_resampled.dropna()
        for window in windows:
          df_resampled['SMA_' + str(window)] = df_resampled['Último'].rolling(window=window, min_periods=0).mean()
        return df_resampled
    else:
        return df

def print_group(ticket,df):
    
    color.write('\n' + ticket + ' (' + df.index[-1].strftime("%H:%M") + '): ' ,"TODO")
    for i,window in enumerate(windows):
        color.write('(' + str(window) + ')',"TODO")
        value = round(df['SMA_' + str(window)][-1],3)
        color.write(' ' + str(value) + ' ',windows_color[i])
        

def analysis(df):
    
    global data
    data = get_last_data()        

    grouped_df = df.groupby(["Papel"]).agg(lambda x: ';'.join(x[x.notnull()].astype(str)))
    color.write('\n',"TODO")
    for group in grouped_df.iterrows():        
        ticket = group[0]
        df = create_resampled_from_group(group)                                      
        print_group(ticket,df)
                                           

def run():
    
    reset_data()
    while True:
        df = None
        while df is None:
            df = try_to_get_df()
            time.sleep(1)
        analysis(df)
        time.sleep(3)

def test():
    df = None
    while df is None:
        df = try_to_get_df()
        time.sleep(1)
        

    df['Hora'] = df['Hora'].apply(convert_to_datetime)
    df.set_index('Hora', inplace=True)

    date = dt.datetime.strptime('2022-02-07 11:30:00','%Y-%m-%d %H:%M:%S')    

    reset_data()
    for i in range(120):
        
        new_date =  date + dt.timedelta(minutes=i)
        df1 = df[df.index < new_date.strftime("%Y-%m-%d %H:%M:%S")].reset_index()
        df1.fillna(0)
        analysis(df1)        
        time.sleep(0)
        
    
test()
