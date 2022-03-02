import pandas as pd
import pdb
import datetime as dt
import Utils as utils
import threading
import mplfinance as mpf
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import warnings
import numpy as np
import pandas_ta as ta
from ScrollableWindow import ScrollableWindow

PICKLE_FILE = 'btc_tickers.plk'
warnings.filterwarnings('ignore')
PERIOD = '5min'
FIBONACCI = [23.6, 38.2, 61.8, 78.6]
STATUS_FILE = 'btc_status.plk'
RESOLUTION = 100

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




    
def analysis(pickle_file):
    
    df1 = utils.try_to_get_df(pickle_file)

    df1.dropna(inplace=True)
        
    
    df1.reset_index(inplace=True)
    df1['Volume'] = df1['Volume'].apply(utils.to_volume)
    
    df1['Hora'] = df1['Hora'].apply(utils.convert_to_datetime)
    df1.set_index('Hora',inplace=True)
    

    
        
    df4 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
    df6 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Máximo'].agg([('max','last')])
    df7 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Mínimo'].agg([('min', 'last')])

    df4 = pd.concat([df4,df6,df7],axis=1)
    
    tickets = get_tickets(df4)

    for i,ticket in enumerate(tickets):
      
        df0 = df4.loc[pd.IndexSlice[:,ticket], :]
        df0.reset_index('Papel',inplace=True)

    
    
        ax = axes[i]
       
        ax.clear()
    
        
        
        df0 = df0.iloc[-RESOLUTION:]

          

        df0['EMA_9'] = df0['close'].ewm(span=9, adjust=False).mean()
        df0['SMA_40'] = df0['close'].rolling(window=40, min_periods=0).mean()

        apds = [mpf.make_addplot(df0['EMA_9'],type='line',color='green',ax=ax,width=0.9),
                mpf.make_addplot(df0['SMA_40'],type='line',color='red',ax=ax,width=0.9),
                mpf.make_addplot(williams_fractal_bullish(df0),type='scatter',ax=ax,color='lime',markersize=10,marker='^'),
                mpf.make_addplot(williams_fractal_bearish(df0),type='scatter',ax=ax,color='red',markersize=10,marker='v'),
                ]

        if df0['max'][-1] > 0 and df0['min'][-1] > 0:
            hlines =[df0['max'][-1],df0['min'][-1]]
         
            for fib in FIBONACCI:
                hlines.append(df0['max'][-1] - (df0['max'][-1] - df0['min'][-1])*fib/100)
        else:
            hlines = []
            
        mpf.plot(df0,type='candle',hlines=dict(hlines=hlines,linestyle='--'),addplot=apds,ax=ax,xrotation=0, datetime_format='%H:%M')
        ax.set_ylabel(ticket,fontsize=20)
            

def run(pickle_file=PICKLE_FILE):
    
    mc = mpf.make_marketcolors(up='cyan',down='fuchsia',inherit=True)
    style  = mpf.make_mpf_style(base_mpf_style='nightclouds',gridstyle='',marketcolors=mc)

    fig = mpf.figure(style=style,figsize=(19,20))

    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.95, 0.95)

    dimension = [40,8]
    positions = [(1,68),(5,72),(81,148),(85,152),(161,220),(165,224),(233,308),(237,312)]
    global axes
    axes = []
    for pos in positions:
        ax = fig.add_subplot(dimension[0],dimension[1],pos)
        axes.append(ax)
       
    a = ScrollableWindow(fig,analysis,pickle_file)


#run()
