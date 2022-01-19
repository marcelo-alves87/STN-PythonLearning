import pandas as pd
import sys
import time
import pdb
import datetime as dt

PICKLE_FILE = 'btc_tickers.plk'
color = sys.stdout.shell
periods = ['20min','17min','15min','13min','10min', '7min','5min','1min']

def join_cells(x):    
    return ';'.join(x[x.notnull()].astype(str))

def timestamp_to_str(x):
    return x.strftime("%H:%M")

def convert_to_datetime(x):
    if x != x: #is nan
        return ''
    else:
        mytime = dt.datetime.strptime(x,'%H:%M:%S').time()
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

def analysis():
   
    df = pd.read_pickle(PICKLE_FILE)
    data = []
    grouped_df = df.groupby(["Papel"]).agg(join_cells)
    for group in grouped_df.iterrows():
        data1 = []
        data1.append(group[0])
        
        list1 = group[1]['Hora'].split(';')
        list2 = group[1]['Último'].split(';')
        df1 = {'Hora' : list1, 'Último' : list2}
        df1 = pd.DataFrame(df1)
        df1['Hora'] = df1['Hora'].apply(convert_to_datetime)
        df1.set_index('Hora', inplace=True)
        for period in periods:
            
            df_resampled = df1.resample(period).last()
            df_resampled['EMA'] = df_resampled['Último'].ewm(span=9, adjust=False).mean()
            df_resampled['SMA'] = df_resampled['Último'].rolling(window=40, min_periods=0).mean()           
            data1.append([df_resampled.index[-1],df_resampled['EMA'][-1] - df_resampled['SMA'][-1]])

            
            
        data.append(data1)
    color.write('\n',"TODO")    
    for group in data:
        
        color.write(group[0] + ':' ,"TODO")        
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
        color.write('\n',"TODO")    

while True:
    analysis()
    time.sleep(30)

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
