import pandas as pd
import pdb
import datetime as dt
import Analysis_Voice as av
import Analysis_Plot as ap
import Utils as utils

PICKLE_FILE = 'btc_tickers.plk'
PERIOD = '5min'

def from_time(df, value=4,time='hours'):
    now = df['Hora'].iloc[-1]
    now = dt.datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
    if time == 'hours':
        delayed = now - dt.timedelta(hours=value)
    elif time == 'minutes':
        delayed = now - dt.timedelta(minutes=value)        
    delayed = dt.datetime.strftime(delayed,'%Y-%m-%d %H:%M:%S')
    return df[df['Hora'] > delayed]

def try_to_get_df():
    try:
        df = pd.read_pickle(PICKLE_FILE)
        return df
    except:
        return None

df = None
while df is None:
    df = try_to_get_df()

df.dropna(inplace=True)


##df['Volume'] = df['Volume'].apply(utils.to_volume)
##df['Hora'] = df['Hora'].apply(utils.convert_to_datetime)
##df.set_index('Hora',inplace=True)
##
##df4 = df.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])


av.reset_data()
date = dt.datetime.strptime('2022-02-10 11:15:00','%Y-%m-%d %H:%M:%S')
for i in range(120):
    new_date =  date + dt.timedelta(minutes=i)
    df1 = df[df['Hora'] < new_date.strftime("%Y-%m-%d %H:%M:%S")]
    av.analysis(df1,PERIOD)
    #ap.analysis(df1)


##def run():
##    
##    reset_data()
##    while True:
##        df = None
##        while df is None:
##            df = try_to_get_df()
##            time.sleep(1)
##        analysis(df)
##        time.sleep(3)
##
##def test():
##    df = None
##    while df is None:
##        df = try_to_get_df()
##        time.sleep(1)
##        
##    
##    df['Hora'] = df['Hora'].apply(convert_to_datetime)
##    df.set_index('Hora', inplace=True)
##
##    date = dt.datetime.strptime('2022-02-10 15:20:00','%Y-%m-%d %H:%M:%S')    
##
##    reset_data()
##    for i in range(120):
##        
##        new_date =  date + dt.timedelta(minutes=i)
##        df1 = df[df.index < new_date.strftime("%Y-%m-%d %H:%M:%S")].reset_index()        
##        analysis(df1)

