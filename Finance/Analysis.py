import pandas as pd
import pdb
import datetime as dt
import Analysis_Voice as anal_v
import Analysis_Plot as ap
import Utils as utils
import threading
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import warnings

warnings.filterwarnings('ignore')
PICKLE_FILE = 'btc_tickers.plk'
PERIOD = '5min'
RESOLUTION = -30
FIBONACCI = [23.6, 38.2, 61.8, 78.6]
def try_to_get_df():
    try:
        df = pd.read_pickle(PICKLE_FILE)
        return df
    except:
        return None

def get_tickets(df):
    tickets = []
    for value in df.index.values:
        if not value[1] in tickets:
            tickets.append(value[1])
    return tickets    

 

df = None
while df is None:
    df = try_to_get_df()

df.dropna(inplace=True)

style  = mpf.make_mpf_style(base_mpf_style='charles',mavcolors=['blue','orange','red'])

fig = mpf.figure(style=style)
plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.95, 0.95)

dimension = [26,7]
positions = [[(1,45),(50,52)],[(5,49),(54,56)], [(64,108),(113,115)],[(68,112),(117,119)], [(127,171),(176,178)]]
axes = []
for pos in positions:
    ax = fig.add_subplot(dimension[0],dimension[1],pos[0])
    av = fig.add_subplot(dimension[0],dimension[1],pos[1], sharex=ax)
    axes.append([ax,av])


anal_v.reset_data()
date = dt.datetime.strptime('2022-02-10 17:45:00','%Y-%m-%d %H:%M:%S')


def analysis(ival):
    new_date =  date + dt.timedelta(minutes=ival)
    df1 = df[df['Hora'] < new_date.strftime("%Y-%m-%d %H:%M:%S")]
    #df1 = df
    
    if ival > 10:
        x = threading.Thread(target=anal_v.analysis, args=(df1,PERIOD,))
        x.start()
    df1.reset_index(inplace=True)
    df1['Volume'] = df1['Volume'].apply(utils.to_volume)
    df1['Hora'] = df1['Hora'].apply(utils.convert_to_datetime)
    df1.set_index('Hora',inplace=True)
        
    df4 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Último'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
    df5 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Volume'].agg([('volume','sum')])
    df6 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Máximo'].agg([('max','last')])
    df7 = df1.groupby([pd.Grouper(freq=PERIOD), 'Papel'])['Mínimo'].agg([('min', 'last')])
                                                                        
    df1 = pd.concat([df4,df5,df6,df7],axis=1)
    
    tickets = get_tickets(df1)

    for i,ticket in enumerate(tickets):
               
        df0 = df1.loc[pd.IndexSlice[:,ticket], :]
        df0.reset_index('Papel',inplace=True)
        ax = axes[i][0]
        av = axes[i][1]
        ax.clear()
        av.clear()

        df0 = df0.iloc[RESOLUTION:]
        
        hlines=[]
        maximum = df0['max'][-1]
        minimum = df0['min'][-1]
        diff = maximum - minimum
        hlines.append(maximum)
        hlines.append(minimum)
        
        for f in FIBONACCI:
            hlines.append(diff*f/100 + minimum)
        
        mpf.plot(df0,hlines=dict(hlines=hlines,colors=['g','r','b','c','k'],linestyle='--'),type='candle',ax=ax,mav=(5,8,13),axtitle=ticket,volume=av, ylabel='', ylabel_lower='',xrotation=0, datetime_format='%H:%M')

    


ani = animation.FuncAnimation(fig, analysis)    
mpf.show()    
    


