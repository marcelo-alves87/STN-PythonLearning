import pandas as pd
import pdb
import datetime as dt
import Utils as utils
import threading
import mplfinance as mpf
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import time
import warnings
import numpy as np
import pandas_ta as ta
from ScrollableWindow import ScrollableWindow
import sys
import math
from Datum import Datum

DATA_FILE = 'btc_data.plk'
PICKLE_FILE = 'btc_tickers.plk'
warnings.filterwarnings('ignore')
PERIODS = ['1min','5min','15min','30min','60min']
FIBONACCI = [23.6, 38.2, 61.8, 78.6]
STATUS_FILE = 'btc_status.plk'
RESOLUTION = 100
color = sys.stdout.shell
data = []
PRICE_ALERT = {'MGLU3' : [5.16,5.06], 'BRFS3' : 15.88, 'CSNA3' : 23.85, 'GGBR4' : 27.85, 'VALE3': 90.27, 'PETR4': 30.93}
def williams_fractal_bullish(df):
    
    signal = []
    df = df['low']
    len_df = len(df)
    for i in range(len_df):
        if i > 2 and i < len_df - 2:
            if df.iloc[i] <= df.iloc[i-2] and df.iloc[i] <= df.iloc[i-1] and df.iloc[i] < df.iloc[i+1] and df.iloc[i] < df.iloc[i+2]:
                signal.append(df.iloc[i])
            else:
                signal.append(np.nan)
        else:
            signal.append(np.nan)
        
    return signal

def williams_fractal_bearish(df):
    
    signal = []
    df = df['high']
    len_df = len(df)
    for i in range(len_df):
        if i > 2 and i < len_df - 2:
            if df.iloc[i] >= df.iloc[i-2] and df.iloc[i] >= df.iloc[i-1] and df.iloc[i] > df.iloc[i+1] and df.iloc[i] > df.iloc[i+2]:
                signal.append(df.iloc[i])
            else:
                signal.append(np.nan)
        else:
            signal.append(np.nan)
        
    return signal

def get_tickets(df):
    tickets = []
    for value in df.index.values:
        if not value[1] in tickets:
            tickets.append(value[1])
    return tickets    


def group_by_period(df1,period):
    
    df4 = df1.groupby([pd.Grouper(freq=period), 'Papel'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
    df6 = df1.groupby([pd.Grouper(freq=period), 'Papel'])['Máximo'].agg([('max','last')])
    df7 = df1.groupby([pd.Grouper(freq=period), 'Papel'])['Mínimo'].agg([('min', 'last')])

    df4 = pd.concat([df4,df6,df7],axis=1)

    return df4

def save_datum(datum,flag):
    
    index = data.index(datum)
    data[index].flag = flag

def notify(ticket,status,index):
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
    elif status == 3:
       color.write('\n(' + time1 + ') ** ' + ticket + ' **','KEYWORD')
       text = 'Strike'
       path1 = 'Utils/Strike.mp3'   
    

    utils.play(text,path1,'en-us')

def check_mavs(ticket,mavs,time1):
    if mavs[1] < 0:       
        return 1
    elif mavs[1] > 0:
        
        return 2
    else:
        return 0

def strategy(ticket,mavs,time1):
    datum = Datum(ticket)
    b = check_mavs(ticket,mavs,time1)
    if datum in data:
        index = data.index(datum)       
        if data[index].flag is True and b == 1:
            notify(ticket,1,time1)
            data[index].flag = False
        elif data[index].flag is False and b == 2:
            notify(ticket,2,time1)
            data[index].flag = True
        elif b == 0:
            #data[index].flag = False
            pass
    else:        
        data.append(datum)
        
def check_price(price, ticket, df):
    if price >= df['low'][-1] and price <= df['high'][-1]:
            notify(ticket,3,df.index[-1])
            del PRICE_ALERT[ticket]
  

def price_alert(ticket,df):
    if ticket in PRICE_ALERT:
        
        price = PRICE_ALERT[ticket]
        if isinstance(price,list):
            
            check_price(price[0],ticket,df)
            check_price(price[1],ticket,df)
        else:
            check_price(price,ticket,df)
        
    
def analysis(pickle_file, fibonacci = False):
    
    df1 = utils.try_to_get_df(pickle_file)

    df1.dropna(inplace=True)
        
    
    df1.reset_index(inplace=True)
    df1['Volume'] = df1['Volume'].apply(utils.to_volume)
    
    df1['Hora'] = df1['Hora'].apply(utils.convert_to_datetime)
    df1.set_index('Hora',inplace=True)
    
    
    dfs = []
    for period in PERIODS:
        dfs.append(group_by_period(df1,period))

    tickets = df1.groupby('Papel').first().index.to_list()
   

    for i,ticket in enumerate(tickets):
        
        df0 = dfs[1].loc[pd.IndexSlice[:,ticket], :]
        df0.reset_index('Papel',inplace=True)
        df0['EMA_9'] = df0['close'].ewm(span=9, adjust=False).mean()
        df0['SMA_40'] = df0['close'].rolling(window=40, min_periods=0).mean()        
        df0 = df0.iloc[-RESOLUTION:]

        mavs = []
        for df in dfs:            
            df2 = df.loc[pd.IndexSlice[:,ticket], :]
            df2.reset_index('Papel',inplace=True)
            if len(df2.index) > 40:
                df2['EMA_9'] = df2['close'].ewm(span=9, adjust=False).mean()
                df2['SMA_40'] = df2['close'].rolling(window=40, min_periods=0).mean()
                mavs.append(round(df2['EMA_9'][-1] - df2['SMA_40'][-1],2))
            else:
                mavs.append(0)
            
        
        strategy(ticket,mavs,df2.index[-1])
        price_alert(ticket,df0)
        ax = axes[i]
       
        ax.clear() 
        
                

        apds = [mpf.make_addplot(df0['EMA_9'],type='line',color='green',ax=ax,width=0.9),
                mpf.make_addplot(df0['SMA_40'],type='line',color='red',ax=ax,width=0.9),
                mpf.make_addplot(williams_fractal_bullish(df0),type='scatter',ax=ax,color='lime',markersize=10,marker='^'),
                mpf.make_addplot(williams_fractal_bearish(df0),type='scatter',ax=ax,color='red',markersize=10,marker='v'),
                ]

        if df0['max'][-1] > 0 and df0['min'][-1] > 0:
            hlines =[df0['max'][-1],df0['min'][-1]]
            
        if fibonacci:  
           for fib in FIBONACCI:
               hlines.append(df0['max'][-1] - (df0['max'][-1] - df0['min'][-1])*fib/100)
        else:
            hlines = []
            
        mpf.plot(df0,type='candle',hlines=dict(hlines=hlines,linestyle='--'),addplot=apds,ax=ax,xrotation=0, datetime_format='%H:%M')
        ax.set_ylabel(ticket,fontsize=20)

        handles = []
        for mav in mavs:
          if mav > 0:   
            green = mlines.Line2D([], [], color='green', marker='^', linestyle='None',
                          markersize=10, label=mav)
            handles.append(green)
          else:  
            red = mlines.Line2D([], [], color='red', marker='v', linestyle='None',
                          markersize=10, label=mav)
            handles.append(red)   

        ax.legend(handles=handles,loc='upper left')
        
          

def run(pickle_file=PICKLE_FILE):
    
    mc = mpf.make_marketcolors(up='cyan',down='fuchsia',inherit=True)
    style  = mpf.make_mpf_style(base_mpf_style='nightclouds',gridstyle='',marketcolors=mc)

    fig = mpf.figure(style=style,figsize=(19,20))

    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.95, 0.95)

    
    df1 = utils.try_to_get_df(pickle_file)
    ntickets = len(df1.groupby('Papel').first().index.to_list())
    
    positions = []
    j1 = 0
    
    for i in range(ntickets):
        if ntickets % 2 != 0 and i == ntickets - 1:
            positions.append((j1 + 1,j1 + 68))
            j1 += 80 
        elif i % 2 == 0:            
            positions.append((j1 + 1,j1 + 68))
            positions.append((j1 + 5,j1 + 72))
            j1 += 80    
    
            
    dimension = [j1/8,8]
    
    global axes
    axes = []
    for pos in positions:
        ax = fig.add_subplot(dimension[0],dimension[1],pos)
        axes.append(ax)
       
    a = ScrollableWindow(fig,analysis,pickle_file)


run()
