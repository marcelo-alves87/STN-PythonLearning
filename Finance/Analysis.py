import pandas as pd
import sys
import time
import pdb
import datetime as dt

PICKLE_FILE = 'btc_tickers.plk'
color = sys.stdout.shell
periods = ['15min','13min','11min','9min','7min','5min','3min','1min'] # deve ser em ordem decrescente

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
        try:
            mytime = dt.datetime.strptime(x,'%H:%M:%S').time()
        except:
            mytime = dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S').time()
            
        date = dt.datetime.combine(dt.date.today(), mytime)
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

def analysis(df):
    data = []
    grouped_df = df.groupby(["Papel"]).agg(join_cells)
    for group in grouped_df.iterrows():
        
        lev = group[1]['Lev.'].split(';')[0]
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df1 = {'Hora' : list1, 'Último' : list2}
        df1 = pd.DataFrame(df1)
        df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
        df1.set_index('Hora', inplace=True)
        
        if len(df1) > 1:
            data1 = []
            data1.append([group[0],lev])
            for period in periods:
                
                df_resampled = df1.resample(period).last()
                df_resampled['EMA'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
                ema_qt = len(df_resampled['EMA'])
                df_resampled['SMA'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()
                sma_qt = len(df_resampled['SMA'])

                if ema_qt < 9:
                    value = ema_qt
                elif sma_qt < 40:
                    value = sma_qt
                else:
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

    data.sort(key=sort, reverse=True)
    
    for group in data:                
        color.write(group[0][0] + '(' + group[0][1] + ')' + ':' ,"TODO")        
        for i,period in enumerate(periods):
            color.write(' ' + period + '(' + timestamp_to_str(group[i + 1][0]) + ') ',"TODO")
            value = group[i + 1][1]
            value_str =str(round(abs(value),3))
             
            if value > 0:
                color.write(value_str,"STRING")    
            elif value < 0:
                color.write(value_str,"COMMENT")
            else:
                color.write(value_str,"KEYWORD")
            
            if len(group[i + 1]) > 2:
                value = group[i + 1][2]
                if value == 'G':
                    color.write(' *',"STRING")    
                elif value == 'R':
                    color.write(' *',"COMMENT")
                
        color.write('\n',"TODO") 

while True:
    df = pd.read_pickle(PICKLE_FILE)
    analysis(df)
    time.sleep(10)
       
    
##df = pd.read_pickle(PICKLE_FILE)
##df['Hora'] = df['Hora'].apply(convert_to_datetime)
##df.set_index('Hora', inplace=True)
##df = df[df.index < '17:40:00']
##analysis_(df.reset_index())
## Testing 
##df = pd.read_pickle(PICKLE_FILE)
##
##df  = df.iloc[:-1000]
##
##papel = 'JBSS3'
##
##grouped_df = df.groupby(["Papel"]).agg(join_cells)
##df2 = grouped_df[grouped_df.index == papel]
##list1 = df2['Hora'].values
##list2 = df2['Último'].values
##df1 = {'Hora' : list1[0].split(';'), 'Último' : list2[0].split(';')}
##df1 = pd.DataFrame(df1)
##df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
##df1.set_index('Hora', inplace=True)
##
##
##color.write(papel + ' : ' ,"TODO") 
##for period in periods:
##    
##    df_resampled = df1.resample(period).last()
##    df_resampled['EMA'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
##    df_resampled['SMA'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()           
##
##    color.write(' ' + period + '(' + timestamp_to_str(df_resampled.index[-1]) + ') ->',"TODO")
##    value = df_resampled['EMA'][-1] - df_resampled['SMA'][-1]
##    value_str = ' ' + str(round(abs(value),3))
##    if value > 0:
##        color.write(value_str,"STRING")    
##    elif value < 0:
##        color.write(value_str,"COMMENT")
##    else:
##        color.write(value_str,"KEYWORD")
##    #data1.append([,])
##
##
##
####list2 = group[1]['Último'].split(';')
####df1 = {'Hora' : list1, 'Último' : list2}
####df1 = pd.DataFrame(df1)
####print(df1)
##
