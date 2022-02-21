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


mc = mpf.make_marketcolors(up='cyan',down='fuchsia',inherit=True)
style  = mpf.make_mpf_style(base_mpf_style='nightclouds',gridstyle='',marketcolors=mc)

fig = mpf.figure(style=style,figsize=(20,20))

plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.95, 0.95)

dimension = [29,8]
positions = [[(1,52),(57,68)],[(5,56),(61,72)], [(81,132),(137,148)],[(85,136),(141,152)],[(163,214),(219,230)]]
axes = []
for pos in positions:
    ax = fig.add_subplot(dimension[0],dimension[1],pos[0])
    ar = fig.add_subplot(dimension[0],dimension[1],pos[1], sharex=ax)
    axes.append([ax,ar])


def analysis(ival,fargs):
    
    df1 = utils.try_to_get_df(fargs)

    df1.dropna(inplace=True)
        
    
    df1.reset_index(inplace=True)
    df1['Volume'] = df1['Volume'].apply(utils.to_volume)
    
    df1['Hora'] = df1['Hora'].apply(utils.convert_to_datetime)
    df1.set_index('Hora',inplace=True)
        
    df4 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
    df5 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Volume'].agg([('volume','mean')])
    df6 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Máximo'].agg([('max','last')])
    df7 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Mínimo'].agg([('min', 'last')])
                                                                        
    df1 = pd.concat([df4,df5,df6,df7],axis=1)
    
    tickets = get_tickets(df1)

    for i,ticket in enumerate(tickets):
               
        df0 = df1.loc[pd.IndexSlice[:,ticket], :]
        df0['volume'] = df0['volume'].diff()
        df0.fillna(0,inplace=True)
        
        df0.reset_index('Papel',inplace=True)

        df0['SMA_21'] = df0['close'].rolling(window=21, min_periods=0).mean()
        df0['SMA_50'] = df0['close'].rolling(window=50, min_periods=0).mean()
        df0['SMA_200'] = df0['close'].rolling(window=200, min_periods=0).mean()
        df0['rsi'] = utils.RSI(df0['close'])
        df0['rsi_50'] = 50
        
        ax = axes[i][0]
        ar = axes[i][1]
        ax.clear()
        ar.clear()

        df0 = df0.iloc[-RESOLUTION:]
        

        
        apds = [mpf.make_addplot(df0['rsi'],ax=ar,color='yellow',ylim=(10,90)),
                mpf.make_addplot(df0['rsi_50'],ax=ar,color='orange',type='line'),
                mpf.make_addplot(df0['SMA_21'],type='line',color='mediumpurple',ax=ax,width=0.9),
                mpf.make_addplot(df0['SMA_50'],type='line',color='orange',ax=ax,width=0.9),
                mpf.make_addplot(df0['SMA_200'],type='line',color='white',ax=ax,width=0.9),
                mpf.make_addplot(williams_fractal_bullish(df0),type='scatter',ax=ax,color='lime',markersize=10,marker='^'),
                mpf.make_addplot(williams_fractal_bearish(df0),type='scatter',ax=ax,color='red',markersize=10,marker='v'),]



         
            
        
        mpf.plot(df0,type='candle',addplot=apds,ax=ax,ylabel=ticket,xrotation=0, datetime_format='%H:%M')
        
    

def run(pickle_file=PICKLE_FILE):

    ani = animation.FuncAnimation(fig, analysis, fargs=[pickle_file])

    mpf.show()    
    

run()
