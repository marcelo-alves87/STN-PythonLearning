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

PICKLE_FILE = 'btc_tickers.plk'
color = sys.stdout.shell
periods = ['30min','15min','5min','1min'] # deve ser em ordem decrescente
previous_value = None
main_period = None

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
    

def notificate(ticket, beep1):
    
    beepy.beep(beep1)
    
    print_stars(text='WIN')    
    path = 'Utils/' +  ticket + '.mp3'
    language = 'pt-br'        
    myobj = gTTS(text=ticket, lang=language)

    try:
        myobj.save(path)
    except:
        pass
    
    mixer.init()
    mixer.music.load(path)
    mixer.music.play()
    
    
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

def print_group(period, group, index):
    color.write(' ' + period + '->' ,"TODO")
    calc_pct_last_diff(group[index][1],group[index][2])
        
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
    color.write('*',"STRING")
    color.write('*',"COMMENT")
    color.write(text,"TODO")
    color.write('*',"STRING")
    color.write('*',"COMMENT")
    color.write('*',"TODO")
    
data_ = []


def strategy(ticket, data, period):
    
    if period == '5min' and ticket in ['MGLU3','PETR4']:
        data1 = data[periods.index(period):]
        if any(data1) is False or all(data1) is True:
             notificate(ticket, 5)             
    elif period == '15min':
        data1 = data[periods.index(period):]
        if any(data1) is False or all(data1) is True:
            notificate(ticket, 6)            
    # fazer else da Estratégia 1 quando 30 min está disponivel         


def analysis_period(df, ticket, period):
    global previous_value
    
    grouped_df = df.groupby(["Papel"]).agg(join_cells)
    for group in grouped_df.iterrows():
        if ticket == group[0]:
            list1 = group[1]['Hora'].split(';')
            list2 = group[1]['Último'].split(';')
            df1 = {'Hora' : list1, 'Último' : list2}
            df1 = pd.DataFrame(df1)
            df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
            df1['Último'] = df1['Último'].apply(convert_to_float)
            df1.set_index('Hora', inplace=True)
            df_resampled = df1.resample(period).last()
            df_resampled['EMA'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
            df_resampled['SMA'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()
            value = df_resampled['EMA'][-1] - df_resampled['SMA'][-1]
            color.write('\nChecking each ' + period + ' of ' + ticket  + ': (' + timestamp_to_str(df_resampled.index[-1]) + ') ',"TODO")
            value_str = str(round(value, 3))
            if value > 0:
                color.write(value_str,'STRING')
            else:
                color.write(value_str,'COMMENT')
            
            if previous_value is not None:
                if (previous_value < 0 and value > 0):
                    beepy.beep(1)
                    color.write(' @@@','STRING')    
                elif(previous_value > 0 and value < 0):                
                    beepy.beep(1)
                    color.write(' $$$','KEYWORD')    
            previous_value = value               
            

def analysis(df):
    data = []
    global main_period
    grouped_df = df.groupby(["Papel"]).agg(join_cells)
    for group in grouped_df.iterrows():
        lev = group[1]['Lev.'].split(';')[0]
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df1 = {'Hora' : list1, 'Último' : list2}
        df1 = pd.DataFrame(df1)
        df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
        df1['Último'] = df1['Último'].apply(convert_to_float)
        df1.set_index('Hora', inplace=True)
        
        if len(df1) > 1:
            data1 = []
            data1.append([group[0],lev])
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
                    data1.append([df_resampled.index[-1],value])     
                
            data.append(data1)
                
    color.write('\n',"TODO")

    
    for group in data:
        
        score = 0
        len_periods = len(periods) - 1

        for i in range(len_periods):
            if isinstance(group[i + 1][1], int):
                group[i + 1].append('R')
            elif not isinstance(group[i + 2][1], int):
                if (group[i + 1][1] > 0 and group[i + 2][1] > 0) or (group[i + 1][1] < 0 and group[i + 2][1] < 0):
                    score += 1
                    group[i + 1].append('G')
                elif (group[i + 1][1] > 0 and group[i + 2][1] < 0) or (group[i + 1][1] < 0 and group[i + 2][1] > 0):
                    group[i + 1].append('R')
        group.append(score)            

    #data.sort(key=sort)
    
    for group in data:
        check_all_bools = False
        bools = []
        color.write(group[0][0] + '(' + group[0][1] + ')' + ':' ,"TODO")        
        for i,period in enumerate(periods):
            datum = Datum(group[0][0],period,group[i + 1][1])
            if not datum in data_:
                data_.append(datum)
                emph = False
            else:
                datum2 = data_[Datum == datum]
                if (datum.value > 0 and datum2.value < 0) or (datum.value < 0 and datum2.value > 0):
                    emph = True
                else:    
                    emph = False
                data_.remove(datum2)
                data_.append(datum)
                
            color.write(' ' + period + '(' + timestamp_to_str(group[i + 1][0]) + ') ',"TODO")
            value = group[i + 1][1]
            value_str =str(round(abs(value),3))

            
            if emph:                
                check_all_bools = True
                main_period = period
                print_stars()
                if value > 0:
                    bools.append(True)                
                elif value < 0:
                    bools.append(False)                
            else:
                if value > 0:
                        bools.append(True)
                        color.write(value_str,"STRING")
                elif value < 0:
                        bools.append(False)
                        color.write('-' + value_str,"COMMENT")
                
            if len(group[i + 1]) > 3:
                value = group[i + 1][3]
                if value == 'G':
                    color.write(' *',"STRING")    
                elif value == 'R':
                    color.write(' *',"KEYWORD")

        
        if check_all_bools:
            strategy(group[0][0], bools, main_period)
                                
        color.write('\n',"TODO") 

def run():
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

    date = dt.datetime.strptime('2022-02-02 14:30:00','%Y-%m-%d %H:%M:%S')    
    ##start =  date + dt.timedelta(days=interval)    
    ##tomorrow = now + dt.timedelta(days=1)
    ##date.strftime("%Y-%m-%d %H:%M:%S")
    
    for i in range(120):
        new_date =  date + dt.timedelta(minutes=i)
        df1 = df[df.index < new_date.strftime("%Y-%m-%d %H:%M:%S")].reset_index()
        analysis(df1)
        #analysis_period(df1,'MGLU3','5min')
        time.sleep(0)
        
    
test() 


