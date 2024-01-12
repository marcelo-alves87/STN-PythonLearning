import pandas as pd
import pdb
import time
import datetime as dt
import warnings
import os
import json
import sys
import datetime as dt
import pickle
import pandas_datareader.data as web
import yfinance as yfin
import shutil
import mplfinance as mpf
import matplotlib.dates as mdates
import matplotlib.animation as animation

yfin.pdr_override()

MAIN_DF_FILE = 'main_df.pickle'
LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786, 1]

            
def get_data_from_yahoo(ticket, actual_date):
   
   if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')
   start_date = actual_date - dt.timedelta(days=15)   
   end_date = actual_date + dt.timedelta(days=1)   
   # just in case your connection breaks, we'd like to save our progress!
   if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      try:
         ticket = format_ticket(ticket)
         print('{}'.format(ticket))
         df = web.get_data_yahoo(ticket + '.SA', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval= '5m')
         df.reset_index(inplace=True)
         df.to_csv('stock_dfs/{}.csv'.format(ticket))           
      except:
         print(ticket,'not found')
   else:
      print('Already have {}'.format(ticket))

def format_ticket(ticket):
   ticket = ticket.split(' ')
   if len(ticket) == 2:
      ticket = ticket[1]
   else:
      ticket = ticket[0]
   return ticket

def format_volume(vol):
    if vol / 10**9 >= 1:
        return str(round(vol / 10**9,3)) + ' B'
    elif vol / 10**6 >= 1:
        return str(round(vol / 10**6,3)) + ' M'
    elif vol / 10**3 >= 1:
        return str(round(vol / 10**3,3)) + ' k'
    else:
        return vol

def update(df):
   data = []
   df3 = df['Ativo'].drop_duplicates()
   for i in range(len(df3)):
      ticket = format_ticket(df3[i])
      get_data_from_yahoo(ticket, df[df['Ativo'] == df3[i]].index[0])      
      if os.path.exists('stock_dfs/{}.csv'.format(ticket)):
         df4 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
         for index,row in df4.iterrows():
            _data = {'Data/Hora' : to_timezone(row['Datetime']), 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Close'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : row['Volume'], 'Estado Atual' : 'Aberto'}
            data.append(_data)            
   df4 =  pd.DataFrame(data)
   df4['Data/Hora'] = pd.to_datetime(df4['Data/Hora'])
   df4.set_index('Data/Hora', inplace=True)
   df4.sort_index(inplace=True)
   return df4      


def get_tickets():
   data = []
   #data.append('IBOV')
   with open("Tickets.txt") as file:
    for line in file:
        ticket = line.rstrip() 
        data.append(ticket)
   return data

def remove(list, item):
    try:
        list.remove(item)
    except:
        pass

def fibonnaci(x):
    if x == 0 or x == 1:
        return 1
    else:
        return fibonnaci(x - 1) + fibonnaci(x - 2)



def to_timezone(row):
    delta = 0
    try:
        row = dt.datetime.strptime(row, '%Y-%m-%d %H:%M:%S')
        return row
    except:        
        if '-02:00' in row:
            delta = 1
        row = dt.datetime.strptime(row, '%Y-%m-%d %H:%M:%S%z')
        row -= dt.timedelta(hours=delta)   
        str1 = row.strftime('%Y-%m-%d %H:%M:%S')
        return dt.datetime.strptime(str1, '%Y-%m-%d %H:%M:%S')


def make_fibonnaci(name, df, last_date):
    
    lvls = []
    t_lvls = []
    df = df[df['Ativo'] == name]
    
    df_today = df[(df.index >= last_date.strftime('%Y-%m-%d 10:00:00')) & (df.index <= last_date.strftime('%Y-%m-%d 18:00:00'))]    
    df_last = df[df.index <= (last_date - dt.timedelta(days = 1)).strftime('%Y-%m-%d 18:00:00')]

    if not df_last.empty:
        df_last = df_last[df_last.index > df_last.index[-1].strftime('%Y-%m-%d')]
    else:
        df_last = df_today

    lvls_ = [0, 1]

    if df_today['Close'].max() > df_last['High'].max():
        lvls_.append(2)
    
    if df_today['Close'].min() < df_last['Low'].min():
        lvls_.append(-0.236)
        lvls_.append(-0.382)
        
    for j in range(len(lvls_)):
        lvl =  df_last['High'].max() - df_last['Low'].min()
        lvl = lvls_[j]*lvl +  df_last['Low'].min()
        lvls.append(lvl)

##    if not df_today.empty and not df_last.empty:
##
##        #lvls_ = [2]
##        lvls_ = [0, 0.236, 0.382, 0.5, 0.681, 0.786, 1, 1.236, 1.382, 1.5, 1.681, 1.786, 2, 2.236, 2.382]
##            
##        t_diff = abs(df_last[df_last['High'] == df_last['High'].max()].index[0] - df_last[df_last['Low'] == df_last['Low'].min()].index[0])
##        t_diff2 = df_today.index[0] - df_last.index[-1] - dt.timedelta(minutes = 5)
##        t_min = min(df_last[df_last['High'] == df_last['High'].max()].index[0],df_last[df_last['Low'] == df_last['Low'].min()].index[0])
##
##    
##        for j in range(len(lvls_)):
##            t_lvl = lvls_[j] * t_diff + t_min + t_diff2
##            if t_lvl > df_today.index.min() and t_lvl < df_today.index.max(): 
##                t_lvls.append(t_lvl)
            
    
    return lvls, t_lvls

def plot(tickers, verbose=False):
    s  = mpf.make_mpf_style(base_mpf_style='charles',gridaxis='both',y_on_right=False)
    fig = mpf.figure(figsize=(12,9), style=s)
    l = len(tickers)
    axis = {}
    main_df = pd.DataFrame()
    for i in range(l):        
        if os.path.exists('stock_dfs/{}.csv'.format(tickers[i])):
            df = pd.read_csv('stock_dfs/{}.csv'.format(tickers[i]))
            df.reset_index(inplace=True)
            df['Datetime'] = df['Datetime'].apply(lambda row: to_timezone(row))
            df['Ativo'] = tickers[i] 
            df['EMA_1'] = df['Close'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
            df['EMA_2'] = df['Close'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

            df = df[['Ativo','Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close','Volume', 'EMA_1', 'EMA_2']]

            df.index = pd.DatetimeIndex(df['Datetime'])

            df = df[['Ativo', 'Open', 'High', 'Low', 'Close', 'Adj Close','Volume', 'EMA_1', 'EMA_2']]

            if main_df.empty:
                main_df = df
            else:
                main_df = pd.concat([main_df, df])
    
    first_date =  main_df.index[0]
    last_date = main_df.index[-1]
    for i in range(l):
        if i == 0:
            axis[i] = fig.add_subplot(l,1,i + 1)
        else:
            axis[i] = fig.add_subplot(l,1,i + 1, sharex=axis[0])

    dfs = {}    
    while last_date > first_date:
      
        for i in range(l): 
            axis[i].clear()
            if i == 0:
                axis[i].set_title(last_date.strftime('%Y-%m-%d'))
                df2 = pd.DataFrame()
            if i != l - 1:
                axis[i].get_xaxis().set_visible(False)
            
            df = main_df[main_df['Ativo'] == tickers[i]]
            df = df[df.index > last_date.strftime('%Y-%m-%d')]
            df = df[df.index < (last_date + dt.timedelta(days = 1)).strftime('%Y-%m-%d')]

            if df2.empty:
                df2 = df
            else:
                df2 = pd.concat([df2, df])
            
            #axis[i].xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30]))

            apd_1 = mpf.make_addplot(df['EMA_1'],type='line', ax=axis[i], color='blue')
            apd_2 = mpf.make_addplot(df['EMA_2'],type='line', ax=axis[i], color='darkblue')

            lvls, t_lvls = make_fibonnaci(tickers[i], main_df, last_date)

            mpf.plot(df,ax=axis[i], ylabel=tickers[i], type='candle', addplot=[apd_1,apd_2],\
                                  hlines=dict(hlines=lvls,\
                                              colors=['red','green', 'y', 'orange','purple','blue'],\
                                              alpha=0.8,linestyle='--'),    show_nontrading=True , vlines=dict(vlines=t_lvls,linewidths=(1,2,3, 4, 5 ,6)))
            
        if not df.empty:
            fig.savefig('plots/{}.png'.format(last_date.strftime('%Y-%m-%d')))

            def count_groups(df):
                group = []
                if not df.empty:
                    s1 = df.index - pd.Series(df.index).shift()
                    indexes = s1[s1 != 1].index
                    for i in range(len(indexes) - 1):
                        group.append(indexes[i + 1] - indexes[i])                        
                    group.append(len(df) - sum(group))
                return group
                
            
            if verbose:
                print('***************')
                print(df2.index[-1].strftime('%Y-%m-%d'))
                print('***************')

                for j in range(l):

                    df4 = df2.reset_index()

                    print(count_groups(df4[(df4['Ativo'] == tickers[j]) & (df4['EMA_1'] > df4['EMA_2'])]))
                    print(count_groups(df4[(df4['Ativo'] == tickers[j]) & (df4['EMA_1'] < df4['EMA_2'])]))

                
        last_date -= dt.timedelta(days = 1)        
        #time.sleep(1)
        
    #mpf.show()




def day_trade(tickers):
    global main_df, shift, frame
    s  = mpf.make_mpf_style(base_mpf_style='charles',gridaxis='both',y_on_right=False)
    fig = mpf.figure(figsize=(5,9), style=s)
    l = len(tickers)
    axis = {}
    main_df = pd.DataFrame()
    ani_running = True
    shift = 0
    frame = 0
    for i in range(l):        
        if os.path.exists('stock_dfs/{}.csv'.format(tickers[i])):
            df = pd.read_csv('stock_dfs/{}.csv'.format(tickers[i]))
            df.reset_index(inplace=True)
            df['Datetime'] = df['Datetime'].apply(lambda row: to_timezone(row))
            df['Ativo'] = tickers[i] 
         
            df = df[df['Datetime'] > '2023-12-16']
            
            df = df[['Ativo','Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close','Volume']]

            df.index = pd.DatetimeIndex(df['Datetime'])

            if main_df.empty:
                main_df = df
            else:
                main_df = pd.concat([main_df, df])
   
    for i in range(l):
        if i == 0:
            axis[i] = fig.add_subplot(l,1,i + 1)
        else:
            axis[i] = fig.add_subplot(l,1,i + 1, sharex=axis[0])
   
    dates = main_df['Datetime'].dt.date.drop_duplicates()
    
    def custom_plot():
        global _ival, shift
        if _ival < len(dates):
            for i in range(l): 
                axis[i].clear()
                if i != l - 1:
                    axis[i].get_xaxis().set_visible(False)
                    axis[i].set_title(dates[_ival].strftime('%Y-%m-%d'))
                        
                        
                df = main_df[(main_df['Ativo'] == tickers[i]) &\
                                  (main_df.index.date == dates[_ival])]

                c1 = [df.index[1], df.index[2], df.index[3], df.index[5], df.index[8], df.index[13], df.index[21], df.index[34], df.index[55]]

                c1 = [x + dt.timedelta(minutes=5*shift) for x in c1]

                h1 = []
                
                if _ival == 0:
                    diff = df['High'].max() - df['Low'].min()
                    for k in LEVELS:
                        h1.append(round(df['Low'].min() + diff*k, 2))
                else:
                    df1 = main_df[(main_df['Ativo'] == tickers[i]) &\
                                  (main_df.index.date == dates[_ival - 1])]
                    diff = df1['High'].max() - df1['Low'].min()
                    for k in LEVELS:
                        h1.append(round(df1['Low'].min() + diff*k,2))

               

                mpf.plot(df,ax=axis[i], ylabel=tickers[i], type='candle', show_nontrading=True, vlines=c1, hlines=h1)
        else:
            exit()
       
    def animate(ival):
        global _ival, frame
        _ival = (ival % len(dates)) + frame
        custom_plot()

    def on_key_press(event):
        global _ival, shift, frame
        nonlocal ani_running
        if event.key == ' ':
            if ani_running:
                ani.event_source.stop()
                frame -= 1
                ani_running = False                
            else:
                ani.event_source.start()
                ani_running = True
        elif event.key == 'right':
            shift += 1
        elif event.key == 'left':
            shift -= 1
            
            
                   
    #fig.savefig('plots/{}.png'.format(last_date.strftime('%Y-%m-%d')))
    fig.canvas.mpl_connect('key_press_event', on_key_press)    
    ani = animation.FuncAnimation(fig, animate, interval=350)     
    
    mpf.show()

def has_bull_fractal(df1, time):
   format = '%Y-%m-%d' + ' ' + time +':%S'
   date = dt.datetime.strptime(df1.index[-1].strftime(format),'%Y-%m-%d %H:%M:%S')
   try:
      df1.reset_index(inplace=True)
      index = df1[df1['Data/Hora'] == date].index[0]   
      value = df1.iloc[index]['Mínimo']
      value0 = df1.iloc[index - 2]['Mínimo']
      value1 = df1.iloc[index - 1]['Mínimo']
      value2 = df1.iloc[index + 1]['Mínimo']
      value3 = df1.iloc[index + 2]['Mínimo']
   except:
      return False
   if value0 > value1 and value1 > value and value < value2 and value2 < value3:
      return True
   else:
      return False
   
def strategy(main_df):
    #12:15
    time = '12:30'
    df = main_df[main_df.index.date == main_df.index[-3].date()]
    print(main_df.index[-3].date().strftime('%Y-%m-%d'))
    for i,ticket in df['Ativo'].drop_duplicates().items():
        df1 = df[df['Ativo'] == ticket]
        vol = df1['Financeiro'].sum()
        
        #df1 = df1[df1['Último'] == df1['Último'].min()]
        if has_bull_fractal(df1, time) and vol >  10**7:
            #12' in df1.index.strftime('%H').values and 
            print(ticket, time, format_volume(vol))
            
def main(update_tickets=False): 
    global count
    #date1 = dt.datetime.now().strftime('%Y-%m-%d')
    date1 = '2024-01-10' 
    if not os.path.exists(MAIN_DF_FILE):
       tickets = get_tickets()
       #tickets = ['PETR4', 'PETR3', 'BBDC4', 'BBDC3', 'GOAU4', 'GGBR4']
       df1 = pd.DataFrame({'Ativo' : tickets, 'Data/Hora' : dt.datetime.strptime(date1 + ' 18:00:00', '%Y-%m-%d %H:%M:%S')})
       df1.set_index('Data/Hora', inplace=True)
       df1 = update(df1)
       df1.dropna(inplace=True)
       df1.to_pickle(MAIN_DF_FILE)
       
    main_df = pd.read_pickle(MAIN_DF_FILE)
    #main_df = main_df[main_df.index <= dt.datetime.strptime(date1, '%Y-%m-%d')]
    if update_tickets:
       main_df = update(main_df)
    main_df.dropna(inplace=True)
   
 
     
    #plot(['GOAU4','GGBR4'])
    #day_trade(['GOAU4','GGBR4'])
    strategy(main_df)
    
def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')           

warnings.simplefilter(action='ignore')
reset(reset_main=False)
main()
