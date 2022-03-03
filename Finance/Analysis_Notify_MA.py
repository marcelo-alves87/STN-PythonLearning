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
DATA_FILE = 'btc_data.plk'
color = sys.stdout.shell
windows_color = ['DEFINITION', 'KEYWORD', 'COMMENT']
PERIOD = '15min'
data = []

def create_resampled_from_group(group):
    if len(group[1]['Hora']) > 0:
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df = pd.DataFrame({'Hora' : list1, 'Último' : list2})
        df['Hora'] = df['Hora'].apply(utils.convert_to_datetime)
        df['Último'] = df['Último'].apply(utils.convert_to_float)
        df.set_index('Hora', inplace=True)
            
        
        df_resampled = df.resample(PERIOD)['Último'].agg([('High','max'),('Low', 'min'),('Último', 'last')])
        df_resampled.dropna(inplace=True)

        df_resampled['SMA_40'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()
        df_resampled['EMA_9'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
        return df,df_resampled
    else:
        return None

def print_group(ticket,df):
    
    color.write('\n' + ticket + ' (' + df.index[-1].strftime("%H:%M") + '): ' ,"TODO")
    for i,window in enumerate(windows):
        color.write('(' + str(window) + ')',"TODO")
        value = round(df['SMA_' + str(window)][-1],3)
        color.write(' ' + str(value) + ' ',windows_color[i])


def notify(ticket,status, index):
    path1 = 'Utils/' + ticket + '.mp3'    
    utils.play(ticket,path1,'pt-br')
    time1 = utils.convert_to_str(index,format='%H:%M')
    if status == 1:
       color.write('\n(' + time1 + ') -- ' + ticket +' --','COMMENT')
       text = 'Down'
       path1 = 'Utils/Down.mp3'    
    elif status == 2:
       color.write('\n(' + time1 + ') ++ ' + ticket + ' ++','STRING')
       text = 'Up'
       path1 = 'Utils/Up.mp3'
       
    

    utils.play(text,path1,'en-us')
    

def save_datum(datum,flag):
    
    index = data.index(datum)
    data[index].flag = flag

    
def bearish_fractal(df):
    if len(df) > 4:
        df = df['High']
        if df.iloc[-3] >= df.iloc[-4] and df.iloc[-3] >= df.iloc[-5] and df.iloc[-3] > df.iloc[-2] and df.iloc[-3] > df.iloc[-1]:
            return True
        else:
            return False
    else:
        return False

def bullish_fractal(df):
    if len(df) > 4:
        df = df['Low']
        if df.iloc[-3] <= df.iloc[-4] and df.iloc[-3] <= df.iloc[-5] and df.iloc[-3] < df.iloc[-2] and df.iloc[-3] < df.iloc[-1]:
            return True
        else:
            return False
    else:
        return False

    
def strategy(ticket,df):
    
    values = []
    ema = df['EMA_9'][-1]
    sma = df['SMA_40'][-1]
    price = df['Último'][-1]
    datum = Datum(ticket)
    if datum in data:
        datum = data[data.index(Datum(ticket))]    

        if ema > sma:
            if datum.flag != 2:
                notify(ticket, 2,df.index[-1])
                save_datum(datum,2)
                
        elif ema < sma:
            if datum.flag != 1:
                notify(ticket,1, df.index[-1])
                save_datum(datum,1)
                 

        elif datum.flag != 0:
            save_datum(datum,0)
               
    else:                
        data.append(datum)

      
             
def analysis(df):
    
    global data    
    data = utils.get_pickle_file(DATA_FILE)
    if data is None:
        data = []
    
    grouped_df = df.groupby(["Papel"]).agg(lambda x: ';'.join(x[x.notnull()].astype(str)))

      
    for group in grouped_df.iterrows():
        
        ticket = group[0]
        df,df_resampled = create_resampled_from_group(group)
        if df is not None:
            #print_group(ticket,df_resampled)
            strategy(ticket,df_resampled)            
     

            
    utils.save_pickle_file(DATA_FILE,data)       
                                               

def run(pickle_file=PICKLE_FILE):
    
    while True:
        df1 = utils.try_to_get_df(pickle_file)  
        df1.dropna(inplace=True)
        
        analysis(df1)
        time.sleep(3)    

#run()

