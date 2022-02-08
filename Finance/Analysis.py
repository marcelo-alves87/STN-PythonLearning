import pandas as pd
import sys
import time
import pdb
import datetime as dt
from Datum import Datum
import beepy
import threading
import os
from gtts import gTTS
from pygame import mixer
import numpy as np
import pickle

PICKLE_FILE = 'btc_tickers.plk'
DATA__FILE = 'btc_data_.plk'
color = sys.stdout.shell
periods = ['60min','30min','15min','5min','1min'] # deve ser em ordem decrescente

def RSI(column):
    #Get just the adjusted close
    # Get the difference in price from previous step
    delta = column.diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    delta = delta[1:]
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
    window_length = 14
    alpha = 1 / window_length
    roll_up = up.ewm(alpha=alpha).mean()
    roll_down = down.ewm(alpha=alpha).mean()
    rs = roll_up / roll_down
    rsi_rma = 100.0 - (100.0 / (1.0 + rs))
    
    return rsi_rma[-1]


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

def play_cima_baixo(value):
    if value > 0: 
        str1 = 'Cima!'                
    else:
        str1 = 'Baixo!'

    path1 = 'Utils/' +  str1 + '.mp3'
    y = threading.Thread(target=play, args=(str1,path1,'pt-br'))
    y.start()
    y.join()

def notificate(ticket, period,value):
    

    index = periods.index(period)
    path1 = 'Utils/' +  ticket + '.mp3'
    path2 = 'Utils/' +  period + '.mp3'

    
    x = threading.Thread(target=play, args=(ticket,path1,'pt-br'))
    x.start()
    x.join()

    if index == 4:
        str1 = 'Reset'        
    elif index == 3:
        str1 = 'Hit'
    elif index == 2:                        
        str1 = 'Special'                      
    elif index == 1:
        str1 = 'Brutality'
    elif index == 0:
        str1 = 'Fatality'

    print_stars(text=str1.upper())             
    y = threading.Thread(target=play, args=(str1,path2,'en-us'))
    y.start()
    y.join()    
        
    
    play_cima_baixo(value)    
         
         
        
        

        
   
def convert_to_date_str(x):    
    x = str(x)
    if len(x) == 1:
        return '0' + x
    else:
        return x
    
def join_cells(x):    
    return ';'.join(x[x.notnull()].astype(str))

def timestamp_to_str(x):
    return x.strftime("%H:%M")

def convert_to_datetime(x):
    
    if x != x: #is nan
        return ''
    elif x == '':
        return ''
    else:
        
        date = dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')           
        
        return date

def print_period(period, timestamp, value):

    my_color = 'TODO'
    
    value_str = str(round(abs(value),3))
    if value < 0:
        my_color = 'COMMENT'
        value_str = '-' + value_str
    else:
        my_color = 'STRING'
        
    
    
    color.write(' ' + period + '(' + timestamp  + ') ', my_color)
    color.write(value_str, my_color)
        
def calc_pct_last_diff(sma,ema):
    value = abs(ema[-1] - sma[-1])
    value = str(ema[-1]) + ' ' + str(sma[-1])
    if ema[-1] > sma[-1]:
        return color.write(value,"STRING")
    elif ema[-1] == sma[-1]:
        return color.write(value,"KEYWORD")
    else:
        return color.write(value,"COMMENT")
    
def resample(df , period):
    
    if pd.isnull(df.index[-1]):
        return None
    else:
        
        df_resampled = df.resample(period).last()
        
        df_resampled['EMA'] = df_resampled['Preco'].ewm(span=9, adjust=False).mean()
        df_resampled['SMA'] = df_resampled['Preco'].rolling(window=40, min_periods=0).mean()           

        return df_resampled.index[-1],df_resampled['SMA'],df_resampled['EMA']

def try_to_get_df():
    try:
        df = pd.read_pickle(PICKLE_FILE)
        return df
    except:
        return None

def sort(x):
    return x[-1]

def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)
    
def print_stars(text=''):
    color.write(' *',"TODO")
    color.write('*',"STRING")
    color.write('*',"COMMENT")
    color.write(text,"TODO")
    color.write('*',"STRING")
    color.write('*',"COMMENT")
    color.write('* ',"TODO")

def find_in_data(ticket,period):
    datum = None
    for datum in data_:
        if datum.ticket == ticket and datum.period == period:
            return datum
    return datum


def get_next_datum(ticket,period):
    
    index = periods.index(period)

    if index == 0:
        return None
    else:
        return find_in_data(ticket,periods[index - 1])

def get_previous_datum(ticket,period):
    
    index = periods.index(period)

    if index == len(periods) - 1:
        return None
    else:
        return find_in_data(ticket,periods[index + 1])
    

def print_data():
    for datum in data_:
        print(datum.ticket,datum.period,datum.value,datum.flag)


def get_last_data_():
    if os.path.exists(DATA__FILE):
         with open(DATA__FILE,"rb") as f:
            return pickle.load(f)
    else:
        return []

def reset_data(reset):
    if reset and os.path.exists(DATA__FILE):
        os.remove(DATA__FILE)    

def notify_price_fibonacci(group,datum):
    
    ticket = group[0]
    price = float(group[1])
    maximum = float(group[2])
    minimum = float(group[3])

    level1 = maximum - ((maximum - minimum) * 0.236)
    level2 = maximum - ((maximum - minimum) * 0.786)

    if price > level1 or price < level2:
        if not datum.flag:
            datum.flag = 1
            beepy.beep(5)
            path1 = 'Utils/' +  ticket + '.mp3'       
            x = threading.Thread(target=play, args=(ticket,path1,'pt-br'))
            x.start()
            x.join()
    else:
        datum.flag = 0

def analysis(df):
    
    global data_
    data_ = get_last_data_()
    data = []
    len_periods = len(periods) - 1
    grouped_df = df.groupby(["Papel"]).agg(join_cells)
    for group in grouped_df.iterrows():        
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        maximum = group[1]['Máximo'].split(';')[-1]
        minimum = group[1]['Mínimo'].split(';')[-1]
        df1 = {'Hora' : list1, 'Último' : list2}
        df1 = pd.DataFrame(df1)        
        df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
        df1['Último'] = df1['Último'].apply(convert_to_float)
        df1.set_index('Hora', inplace=True)
        
        if len(df1) > 1:
            data1 = []
            data1.append([group[0],list2[-1],maximum,minimum])
            for period in periods:
                
                df_resampled = df1.resample(period).last()
                df_resampled = df_resampled.dropna()
                df_resampled['EMA'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
                ema_qt = len(df_resampled['EMA'])
                df_resampled['SMA'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()
                sma_qt = len(df_resampled['SMA'])
                
                if sma_qt < 40:
                    value = sma_qt
                    data1.append([df_resampled.index[-1],value,0])     
                else:
                    rsi = RSI(df_resampled['Último'])
                    value = df_resampled['EMA'][-1] - df_resampled['SMA'][-1]                    
                    data1.append([df_resampled.index[-1],value,rsi])     
                
            data.append(data1)
                
    color.write('\n',"TODO")

    
    for group in data:
        
        
        

        for i in range(len_periods):
            if isinstance(group[i + 1][1], int):
                group[i + 1].append('R')
            elif not isinstance(group[i + 2][1], int):
                if (group[i + 1][1] > 0 and group[i + 2][1] > 0) or (group[i + 1][1] < 0 and group[i + 2][1] < 0):                    
                    group[i + 1].append('G')
                elif (group[i + 1][1] > 0 and group[i + 2][1] < 0) or (group[i + 1][1] < 0 and group[i + 2][1] > 0):
                    group[i + 1].append('R')
        

    #data.sort(key=sort)
    
    for group in data:                
        ticket = group[0][0]
        color.write(ticket + '(' + group[0][1] + ')' + ':' ,"TODO")        
        for i in range(len_periods,-1,-1):
            period = periods[i]
            value = group[i + 1][1]
            rsi = group[i + 1][2]            
            datum = Datum(ticket,period,value)
            time1 = timestamp_to_str(group[i + 1][0])
            if not datum in data_:
                data_.append(datum)
                print_period(period, time1, value)
            else:
                
                datum2 = find_in_data(ticket,period)
                datum.flag = datum2.flag
                prev_datum = get_previous_datum(ticket,period)

                if prev_datum is None:
                    notify_price_fibonacci(group[0],datum)
                
                if (datum.value > 0 and datum2.value < 0) or (datum.value < 0 and datum2.value > 0):
                    
                    

                    print_period(period, time1,value)

                    
                    notificate(ticket,period,value)                   
                             
                    
                else:
                    print_period(period, time1, value)
                    
                data_.remove(datum2)
                data_.append(datum)                 
                
            
      
        
        color.write('\n',"TODO")
        with open(DATA__FILE,"wb") as f:
            pickle.dump(data_,f)

def run(reset=True):
    
    reset_data(reset)    
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

    date = dt.datetime.strptime('2022-02-08 11:30:00','%Y-%m-%d %H:%M:%S')    
    ##start =  date + dt.timedelta(days=interval)    
    ##tomorrow = now + dt.timedelta(days=1)
    ##date.strftime("%Y-%m-%d %H:%M:%S")
    reset_data(True)
    for i in range(120):
        
        new_date =  date + dt.timedelta(minutes=i)
        df1 = df[df.index < new_date.strftime("%Y-%m-%d %H:%M:%S")].reset_index()
        df1.fillna(0)
        analysis(df1)
        #analysis_period(df1,'MGLU3','5min')
        time.sleep(0)
        
    
run()
