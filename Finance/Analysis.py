import pandas as pd
import os
import pdb
import sys
import time
import datetime as dt
import matplotlib.pyplot as plt
import mpl_finance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from Datum import Datum
import threading
from gtts import gTTS
from pygame import mixer
import pickle


PICKLE_FILE = 'btc_tickers.plk'
DATA_FILE = 'btc_data.plk'
color = sys.stdout.shell
windows = [5,8,13]
windows_color = ['DEFINITION', 'KEYWORD', 'COMMENT']
windows_color2 = ['blue', 'yellow', 'red']
period = '5min'
WINDOW_OFFSET = 0.01
MONOTONIC_OFFSET = -3

def play(text, path, language):
    myobj = gTTS(text=text, lang=language)
    try:
        myobj.save(path)
    except:
        pass

    mixer.init()
    mixer.music.load(path)
    mixer.music.play()
    time.sleep(3)

def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)

def convert_to_str(x):
    
      
        return            
        
        return date    

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
    if len(group[1]['Hora']) > 0:
        
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df = pd.DataFrame({'Hora' : list1, 'Último' : list2})
        df['Hora'] = df['Hora'].apply(convert_to_datetime)
        df['Último'] = df['Último'].apply(convert_to_float)
        df.set_index('Hora', inplace=True)
            
        
        df_resampled = df.resample(period).last()
        df_resampled = df_resampled.dropna()
        for window in windows:
            df_resampled['SMA_' + str(window)] = df_resampled['Último'].rolling(window=window, min_periods=0).mean()
        return df,df_resampled
    else:
        return None

def print_group(ticket,df):
    
    color.write('\n' + ticket + ' (' + df.index[-1].strftime("%H:%M") + '): ' ,"TODO")
    for i,window in enumerate(windows):
        color.write('(' + str(window) + ')',"TODO")
        value = round(df['SMA_' + str(window)][-1],3)
        color.write(' ' + str(value) + ' ',windows_color[i])

def notify(ticket,status):
    path1 = 'Utils/' + ticket + '.mp3'    
    x = threading.Thread(target=play, args=(ticket,path1,'pt-br'))
    x.start()
    x.join()

    if status == 0:
       color.write(' * ','TODO')
       text = 'Reset'
       path1 = 'Utils/Reset.mp3'    
    elif status == 1:
       color.write('++ * ++','STRING')
       text = 'Increasing'
       path1 = 'Utils/Increasing.mp3'    
    elif status == 2:
       color.write('-- * --','COMMENT')
       text = 'Decreasing'
       path1 = 'Utils/Decreasing.mp3'
       
    

    y = threading.Thread(target=play, args=(text,path1,'en-us'))
    y.start()
    y.join()

def to_ohlc(x):
    if len(x) == 0:
        return {'open': 0, 'high' : 0, 'low' : 0, 'close': 0, 'volume' : 0}
    return {'open': x[0], 'high' : x.max(), 'low' : x.min(), 'close': x[-1], 'volume' : 0}

def save_datum(datum,flag):
    
    index = data.index(datum)
    data[index].flag = flag
       
def strategy(ticket,df):
    values = []
    for window in windows:
        values.append(df['SMA_' + str(window)][-1])
    datum = Datum(ticket)
    if datum in data:
        datum = data[data.index(Datum(ticket))]    

        if (values[0] < values[1] < values [2]) and (df['SMA_5'].iloc[MONOTONIC_OFFSET:].is_monotonic_decreasing and df['SMA_8'].iloc[MONOTONIC_OFFSET:].is_monotonic_decreasing):
            
            if datum.flag != 2:
                notify(ticket, 2)
                save_datum(datum,2)

        elif (values[0] > values[1] > values[2]) and (df['SMA_5'].iloc[MONOTONIC_OFFSET:].is_monotonic_increasing and df['SMA_8'].iloc[MONOTONIC_OFFSET:].is_monotonic_increasing):

             if datum.flag != 1:
                notify(ticket,1)
                save_datum(datum,1)
             

        elif datum.flag != 0:
            notify(ticket,0)
            save_datum(datum,0)
               
    else:                
        data.append(datum)
        
             
def analysis(df):
    
    global data    
    data = get_last_data()
    df.dropna(inplace=True)
    grouped_df = df.groupby(["Papel"]).agg(lambda x: ';'.join(x[x.notnull()].astype(str)))
    color.write('\n',"TODO")
    for group in grouped_df.iterrows():
        ticket = group[0]
        df,df_resampled = create_resampled_from_group(group)
        if df is not None:
            print_group(ticket,df_resampled)
            strategy(ticket,df_resampled)            
            #plot(ticket,df,df_resampled)

            
    with open(DATA_FILE,"wb") as f:
        pickle.dump(data,f)        
                                               
def plot(ticket,df,df_resampled):

    new_date =  df.index[-1] - dt.timedelta(hours=1)
    
    df = df[df.index > new_date.strftime("%Y-%m-%d %H:%M:%S")]
    
    for window in windows:
        df['SMA_' + str(window)] = df['Último'].rolling(window=window, min_periods=0).mean()

    df_ohlc=df.resample(period).apply(lambda x : to_ohlc(x))
    df_ohlc['open'] = df_ohlc['Último'].apply(lambda x : x['open'])
    df_ohlc['high'] = df_ohlc['Último'].apply(lambda x : x['high'])
    df_ohlc['low'] = df_ohlc['Último'].apply(lambda x : x['low'])
    df_ohlc['close'] = df_ohlc['Último'].apply(lambda x : x['close'])
    df_ohlc['volume'] = df_ohlc['Último'].apply(lambda x : x['volume'])
    df_ohlc.drop(['Último'],1,inplace=True)
    df_ohlc.reset_index(inplace=True)
    df_ohlc['Date'] = df_ohlc['Hora'].map(mdates.date2num)
    df_ohlc.drop(['Hora'],1,inplace=True)
    df_ohlc = df_ohlc[['Date', 'open','high','low','close']]
    
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
    ax1.xaxis_date()
    ax1.set_ylim(df['Último'].min(), df['Último'].max())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    candlestick_ohlc(ax1, df_ohlc.values, colorup='g', width=0.001)
    for i,window in enumerate(windows):
        ax1.plot(df.index, df['SMA_' + str(window)], color = windows_color2[i], linewidth=1, alpha=.8)
        
    
    plt.grid()
    plt.title(ticket)
    plt.show()

    
    

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

    date = dt.datetime.strptime('2022-02-10 15:20:00','%Y-%m-%d %H:%M:%S')    

    reset_data()
    for i in range(120):
        
        new_date =  date + dt.timedelta(minutes=i)
        df1 = df[df.index < new_date.strftime("%Y-%m-%d %H:%M:%S")].reset_index()        
        analysis(df1)
        
        
        
        
    
run()
