from Datum import Datum
import pickle
import sys
import os
import pandas as pd
import Utils as utils
import time
import datetime as dt
import pdb

PICKLE_FILE = 'btc_tickers.plk'
STATUS_FILE = 'btc_status.plk'
DATA_FILE = 'btc_data.plk'
color = sys.stdout.shell
windows = [20,50,100]
windows_color = ['DEFINITION', 'KEYWORD', 'COMMENT']
windows_color2 = ['purple', 'yellow', 'black']
WINDOW_OFFSET = 0.01
MONOTONIC_OFFSET = -5
PERIOD = '1min'

def print_(text,color1,verbose=True):
    if verbose:
        color.write(text,color1)

def reset_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)


def create_resampled_from_group(group,period):
    if len(group[1]['Hora']) > 0:            
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df = pd.DataFrame({'Hora' : list1, 'Último' : list2})
        df['Hora'] = df['Hora'].apply(utils.convert_to_datetime)
        df['Último'] = df['Último'].apply(utils.convert_to_float)
        df.set_index('Hora', inplace=True)
            
        
        df_resampled = df.resample(period).last()
        df_resampled = df_resampled.dropna()
        for window in windows:
            df_resampled['EMA_' + str(window)] = df_resampled['Último'].ewm(span=window, adjust=False).mean()
        return df,df_resampled
    else:
        return None

def print_group(ticket,df):
    
    color.write('\n' + ticket + ' (' + df.index[-1].strftime("%H:%M") + '): ' ,"TODO")
    for i,window in enumerate(windows):
        color.write('(' + str(window) + ')',"TODO")
        value = round(df['EMA_' + str(window)][-1],3)
        color.write(' ' + str(value) + ' ',windows_color[i])


def notify(ticket,status):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    
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
       
    

    utils.play(text,path1,'en-us')
    

def save_datum(datum,flag,status):
    pdb.set_trace()
    index = data.index(datum)
    data[index].flag = flag

    statoos = utils.get_pickle_file(STATUS_FILE)
    if statoos is None:
        statoos = {}
    statoos[datum.ticket] = status
    utils.save_pickle_file(STATUS_FILE,statoos)
    
       
def strategy(ticket,df):
    values = []
    for window in windows:
        values.append(df['EMA_' + str(window)][-1])
    
    datum = Datum(ticket)
    if datum in data:
        datum = data[data.index(Datum(ticket))]    

        if (values[0] < values[1] < values [2]) and (df['EMA_20'].iloc[MONOTONIC_OFFSET:].is_monotonic_decreasing and df['EMA_50'].iloc[MONOTONIC_OFFSET:].is_monotonic_decreasing):
            
            if datum.flag != 2:
                notify(ticket, 2)
                save_datum(datum,2,'Decreasing')

        elif (values[0] > values[1] > values[2]) and (df['EMA_20'].iloc[MONOTONIC_OFFSET:].is_monotonic_increasing and df['EMA_50'].iloc[MONOTONIC_OFFSET:].is_monotonic_increasing):

             if datum.flag != 1:
                notify(ticket,1)
                save_datum(datum,1,'Increasing')
             

        elif datum.flag != 0:
            notify(ticket,0)
            save_datum(datum,0,'Reset')
               
    else:                
        data.append(datum)

      
             
def analysis(df,period=PERIOD,verbose=True):
    
    global data    
    data = utils.get_pickle_file(DATA_FILE)
    if data is None:
        data = []
       
    grouped_df = df.groupby(["Papel"]).agg(lambda x: ';'.join(x[x.notnull()].astype(str)))

    print_('\n',"TODO")
    
    for group in grouped_df.iterrows():
        ticket = group[0]
        df,df_resampled = create_resampled_from_group(group,period)
        if df is not None:
            if verbose:
                print_group(ticket,df_resampled)
            strategy(ticket,df_resampled)            
     

            
    utils.save_pickle_file(DATA_FILE,data)       
                                               

    
       
date = dt.datetime.strptime('2022-02-14 10:15:00','%Y-%m-%d %H:%M:%S')


##for i in range(120):
##    new_date =  date + dt.timedelta(minutes=i)
##    df1 = df[df['Hora'] < new_date.strftime("%Y-%m-%d %H:%M:%S")]
##
##    analysis(df1,'5min')
reset_data()
while True:
    df1 = utils.try_to_get_df(PICKLE_FILE)  
    df1.dropna(inplace=True)
    
    analysis(df1)
    time.sleep(3)
