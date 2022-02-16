import pandas as pd
import pdb
import datetime as dt
import Utils as utils
import threading
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import warnings
import numpy as np

warnings.filterwarnings('ignore')
PERIOD = '1min'
RESOLUTION = -100
FIBONACCI = [23.6, 38.2, 61.8, 78.6]
PICKLE_FILE = 'btc_tickers.plk'
STATUS_FILE = 'btc_status.plk'


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

 

style  = mpf.make_mpf_style(base_mpf_style='yahoo',y_on_right=False,facecolor='darkgray',gridstyle='')

fig = mpf.figure(style=style)
plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.95, 0.95)

dimension = [28,8]
positions = [[(1,60)],[(5,64)], [(81,140)],[(85,144)],[(163,222)]]
axes = []
for pos in positions:
    ax = fig.add_subplot(dimension[0],dimension[1],pos[0])
    #av = fig.add_subplot(dimension[0],dimension[1],pos[1], sharex=ax)
    axes.append([ax])



date = dt.datetime.strptime('2022-02-10 16:45:00','%Y-%m-%d %H:%M:%S')


def analysis(ival):
    df = utils.try_to_get_df(PICKLE_FILE)

    df.dropna(inplace=True)


    #new_date =  date + dt.timedelta(minutes=ival)    
    #df1 = df[df['Hora'] < new_date.strftime("%Y-%m-%d %H:%M:%S")]
    df1 = df
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
        df0['EMA_20'] = df0['close'].ewm(span=20, adjust=False).mean()
        df0['EMA_50'] = df0['close'].ewm(span=50, adjust=False).mean()
        df0['EMA_100'] = df0['close'].ewm(span=100, adjust=False).mean()

        
        
        ax = axes[i][0]
        #av = axes[i][1]
        ax.clear()
        #av.clear()

        df0 = df0.iloc[RESOLUTION:]
        
##        hlines=[]
##        maximum = df0['max'][-1]
##        minimum = df0['min'][-1]
##        diff = maximum - minimum
##        hlines.append(maximum)
##        hlines.append(minimum)
##        
##        for f in FIBONACCI:
##            hlines.append(diff*f/100 + minimum)
        
        apds = [mpf.make_addplot(df0['EMA_20'],type='line',color='purple',ax=ax,width=0.5),
                mpf.make_addplot(df0['EMA_50'],type='line',color='olive',ax=ax,width=0.5),
                mpf.make_addplot(df0['EMA_100'],type='line',color='white',ax=ax,width=0.5),
                mpf.make_addplot(williams_fractal_bullish(df0),type='scatter',ax=ax,color='green',markersize=10,marker='^'),
                mpf.make_addplot(williams_fractal_bearish(df0),type='scatter',ax=ax,color='red',markersize=10,marker='v'),]

##        statoos = utils.try_to_get_df(STATUS_FILE)
##        status1 = ''
##        if ticket in statoos:
##            status1 = statoos[ticket]
##        
        
##        
        mpf.plot(df0,type='candle',addplot=apds,ax=ax,axtitle=ticket,ylabel='', ylabel_lower='',xrotation=0, datetime_format='%H:%M')
        
    


ani = animation.FuncAnimation(fig, analysis)

mpf.show()    
    


