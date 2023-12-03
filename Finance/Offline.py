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
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
count_bull = 0
count_bear = 0
tickets_corr = []
CORR_THRESHOLD = 10
LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786, 1]

#fazer correlação com 30 min ou 15 min e verificar movimentos em 5-min
# most effective 5min ma cross
def verify_trends(main_df):    
    if not main_df.empty:
       df = main_df['Ativo'].drop_duplicates()
       for index,row in df.items():
           if row != 'IBOV':
               df_ticket = main_df[main_df['Ativo'] == row]
               df_ticket.sort_index(inplace=True)
               strategy_candles(row, df_ticket)
               #strategy_ma(row, df_ticket)
            
def get_data_from_yahoo(ticket, actual_date):
   
   if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')
   start_date = actual_date - dt.timedelta(days=55)   
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

def has_great_volume(vol):
    if vol >= 10**6:
        return True
    else:
        return False

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

def strategy_ma(name, df_ticket):
     global count_bull, count_bear
  
     df_ticket['EMA_1'] = df_ticket['Último'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
     df_ticket['EMA_2'] = df_ticket['Último'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

     df_ticket = df_ticket[df_ticket.index >= dt.datetime.strftime(df_ticket.index[-1] - dt.timedelta(days = 115),'%Y-%m-%d')]

     if has_great_volume(df_ticket['Financeiro'][-1]): 
         if df_ticket[df_ticket['EMA_1'] > df_ticket['EMA_2']].empty:
             print(name, 'Bearish', format_volume(df_ticket['Financeiro'][-1]))
             count_bear += 1
         elif df_ticket[df_ticket['EMA_1'] < df_ticket['EMA_2']].empty:
             print(name, 'Bullish', format_volume(df_ticket['Financeiro'][-1]))
             count_bull += 1


def strategy_candles(name, df_ticket):
     global count_bull, count_bear

     df_ticket = df_ticket[df_ticket.index >= dt.datetime.strftime(df_ticket.index[-1] - dt.timedelta(days = 8),'%Y-%m-%d')]
     
     if has_great_volume(df_ticket['Financeiro'][-1]):
         if df_ticket[df_ticket['Abertura'] > df_ticket['Último']].empty:
             tickets_corr.append(name)
             print(name, 'Bullish', format_volume(df_ticket['Financeiro'][-1]))
             count_bull += 1
         elif df_ticket[df_ticket['Abertura'] < df_ticket['Último']].empty:
             tickets_corr.append(name)
             print(name, 'Bearish', format_volume(df_ticket['Financeiro'][-1]))
             count_bear += 1

def correlation(main_df):
    main_df.reset_index(inplace=True)
    df = pd.DataFrame(main_df['Data/Hora'])
    df.drop_duplicates(inplace=True)
    for i in range(len(tickets_corr)):
        df1 = main_df[main_df['Ativo'] == tickets_corr[i]][['Data/Hora', 'Último']]
        df1.rename(columns={'Último': tickets_corr[i]}, inplace=True)
        df = df.merge(df1, on='Data/Hora', how='left')
    df = df[df['Data/Hora'] > df['Data/Hora'].iloc[-7]]
    df_corr = df.corr()
    for index, data in df_corr.iteritems():
        for index1, data1 in data.iteritems():
            if abs(data1) >= 0.992 and index != index1:
                print(('{} e {} fator de correlação: {}').format(index, index1, data1))

    
         
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

def process_data_corr(main_df, verbose=False):
    data = {}
    tickers = main_df['Ativo']
    tickers.drop_duplicates(inplace=True)
    
    for i,ticker in tickers.items():

        
        
        df1 = main_df[main_df['Ativo'] == ticker]
        
        
        df1['EMA_1'] = df1['Último'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
        df1['EMA_2'] = df1['Último'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

        df1 = df1[df1.index > '2023-11-01']

        if not df1.empty:
            date1 = df1.index[0]
            last_date = df1.index[-1]
            
            df2 = df1[df1.index > df1.index[-1].strftime('%Y-%m-%d')]
            volume = (df2['Financeiro'] * df2['Último']).sum()

            if has_great_volume(volume):
                while date1 < last_date:
                    
                    date1_str = dt.datetime.strftime(date1,'%Y-%m-%d')

                    df2 = df1[df1.index > date1_str]
                    
                    df2 = df2[df2.index <  dt.datetime.strptime(\
                        date1_str, '%Y-%m-%d') + dt.timedelta(days = 1)]

                    if not df2.empty:
                        df3 = df2[df2['EMA_1'] > df2['EMA_2']]
                        df4 = df2[df2['EMA_1'] < df2['EMA_2']]
                        if len(df3) <= CORR_THRESHOLD:
                            if date1_str in data:
                                data[date1_str]['Bearish'].append(ticker) 
                            else:
                                data[date1_str] = {'Bearish' : [ticker], 'Bullish' : []}                         
                        elif len(df4) <= CORR_THRESHOLD:
                            if date1_str in data:
                                data[date1_str]['Bullish'].append(ticker) 
                            else:
                                data[date1_str] = {'Bullish' : [ticker], 'Bearish' : []}        
                            
                    date1 += dt.timedelta(days = 1)
    df = pd.DataFrame(data)
    df = df.transpose()
    df.sort_index(inplace=True)
    
    if verbose:
        for i,row in df.iterrows():
            print('----------------')
            print(i)
            print('----------------')
            print('Bullish:')
            print(row['Bullish'])
            print('----------------')
            print('Bearish:')
            print(row['Bearish'])
            print('----------------')
    return df

def process_hit_corr(hit, tickets, df):
    for k,row in df.iterrows():
        for i in range(len(tickets)):
            for j in range(len(tickets)):
                if i > j:
                    index = tickets[i] + ' ' + tickets[j]
                    if (tickets[i] in row['Bearish'] and tickets[j] in row['Bearish'] ) or\
                        (tickets[i] in row['Bullish'] and tickets[j] in row['Bullish']):
                        if index in hit:
                            hit[index] += [k]
                        else:
                            hit[index] = [k]

def process_hit(hit, tickets, df):
    for k,row in df.iterrows():
        for i in range(len(tickets)):
            if tickets[i] in row['Bearish']:
                if tickets[i] in hit:
                    hit[tickets[i]] += [k]
                else:
                    hit[tickets[i]] = [k]
def print_hit(df):
    for i,row in df.iterrows():
        print('----------------')
        print(row[0], row[2])
        for j in range(row[2]):
            print(row[1][j])
        print('----------------')    

def process_hits(main_df):
    df = process_data_corr(main_df, verbose=False)        
    tickets = get_tickets()
    hit = {}
    process_hit_corr(hit, tickets, df)
    #process_hit(hit, tickets, df)
                              
    #with open('hit.pickle', 'wb') as handle:
    #     pickle.dump(hit, handle)
    #with open('hit.pickle', 'rb') as handle:
    #    hit = pickle.load(handle)

    df = pd.DataFrame(hit.items())
    df[2] = df[1].apply(lambda row : len(row))
    df = df.sort_values(2, ascending=False)
    #df[df[2] > 4]
    #df[df[0] == 'FLRY3 BBSE3']
    #print_hit(df[df[2] > 6])
    pdb.set_trace()

def to_timezone(row):
    delta = 0
    try:
        dt.datetime.strptime(row, '%Y-%m-%d %H:%M:%S')
        return row
    except:        
        if '-02:00' in row:
            delta = 1
        row = dt.datetime.strptime(row, '%Y-%m-%d %H:%M:%S%z')
        row -= dt.timedelta(hours=delta)   
        return row.strftime('%Y-%m-%d %H:%M:%S')


def make_fibonnaci(name, df, last_date):
    
    lvls = []
    df = df[df['Ativo'] == name]
    
    df_today = df[(df.index >= last_date.strftime('%Y-%m-%d 10:00:00')) & (df.index <= last_date.strftime('%Y-%m-%d 18:00:00'))]    
    df_last = df[df.index <= (last_date - dt.timedelta(days = 1)).strftime('%Y-%m-%d 18:00:00')]

    if not df_last.empty:
        df_last = df_last[df_last.index > df_last.index[-1].strftime('%Y-%m-%d')]
    else:
        df_last = df_today

    lvls_ = LEVELS.copy()

    if df_today['Close'].max() > df_last['High'].max():
        lvls_.append(1.236)    
        lvls_.append(1.618)
        lvls_.append(2)
    
    if df_today['Close'].min() < df_last['Low'].min():
        lvls_.append(-0.236)    
        lvls_.append(-0.382)    
    
    for j in range(len(lvls_)):
        lvl =  df_last['High'].max() - df_last['Low'].min()
        lvl = lvls_[j]*lvl +  df_last['Low'].min()
        lvls.append(lvl)

    return lvls

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

            #df = df[df['Datetime'] > '2023-10-30']
            #df = df[df['Datetime'] < '2023-10-31']
         
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
            
            axis[i].xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30]))

            apd_1 = mpf.make_addplot(df['EMA_1'],type='line', ax=axis[i], color='blue')
            apd_2 = mpf.make_addplot(df['EMA_2'],type='line', ax=axis[i], color='darkblue')

            lvls = make_fibonnaci(tickers[i], main_df, last_date)

            mpf.plot(df,ax=axis[i], ylabel=tickers[i], type='candle', addplot=[apd_1,apd_2],\
                                  hlines=dict(hlines=lvls,\
                                              colors=['red','brown', 'y', 'orange','purple','green'],\
                                              alpha=0.8,linestyle='--'),    show_nontrading=True)
            
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
    global main_df
    s  = mpf.make_mpf_style(base_mpf_style='charles',gridaxis='both',y_on_right=False)
    fig = mpf.figure(figsize=(5,9), style=s)
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

            df = df[df['Datetime'] > '2023-11-10']
            df = df[df['Datetime'] < '2023-11-11']
         
            df = df[['Ativo','Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close','Volume', 'EMA_1', 'EMA_2']]

            df.index = pd.DatetimeIndex(df['Datetime'])

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
    
    def animate(ival):
        if ival > 0:
            print(ival)
            for i in range(l): 
                axis[i].clear()
                if i != l - 1:
                    axis[i].get_xaxis().set_visible(False)
            
            
                df = main_df[main_df['Ativo'] == tickers[i]]
                index = df.index[0] + dt.timedelta(minutes = 5*ival)
                df = df[df.index <= index]

                apd_1 = mpf.make_addplot(df['EMA_1'],type='line', ax=axis[i], color='blue')
                apd_2 = mpf.make_addplot(df['EMA_2'],type='line', ax=axis[i], color='darkblue')

                mpf.plot(df,ax=axis[i], ylabel=tickers[i], type='candle', addplot=[apd_1,apd_2], show_nontrading=True)
            
            input(index)
            
            
    ani = animation.FuncAnimation(fig, animate, interval=250)     
    
    mpf.show()

def long_short(df, tickets):


  def which_level(pct):
      if isinstance(pct,float):
          if pct > 0:
              decimal = pct % 1
              integer = pct // 1
              i = 0  
              for i in range(len(LEVELS)):
                  if decimal < LEVELS[i]:
                      i += 1
                      break
              return i + integer * len(LEVELS)
          else:
              decimal = pct % -1
              integer = pct // -1
              i = 0  
              for i in range(len(LEVELS)):
                  if decimal > -LEVELS[i]:
                      i += 1
                      break
              return (i + integer * len(LEVELS)) * -1
      else:
          return pct
  dates = df.reset_index()['Data/Hora'].dt.date
  dates = dates.drop_duplicates()
  dates = dates.reset_index()
  dates = dates['Data/Hora']
  for i,row in dates.items():
      if i > 1:
          df1 = df[(df['Ativo'] == tickets[0]) & (df.index.date == dates[i-1])]
          df2 = df[(df['Ativo'] == tickets[-1]) & (df.index.date == dates[i-1])]

          df3 = df[(df['Ativo'] == tickets[0]) & (df.index.date == row)]
          df4 = df[(df['Ativo'] == tickets[-1]) & (df.index.date == row)]

          df3 = pd.DataFrame((df3['Último'] - df1['Mínimo'].min()) / (df1['Máximo'].max() - df1['Mínimo'].min()) )
          df3.rename(columns={'Último': tickets[0]}, inplace=True)  
          df4 = pd.DataFrame((df4['Último'] - df2['Mínimo'].min()) / (df2['Máximo'].max() - df2['Mínimo'].min()) )
          df4.rename(columns={'Último': tickets[-1]}, inplace=True)

          df5 = pd.concat([df3,df4], axis=1)
            
          df5.reset_index(inplace=True)
          print('*******************')  
          print(df5['Data/Hora'].iloc[-1].strftime('%Y-%m-%d'))
          print('*******************')
          for i,row in df5.iterrows():
              level1 = which_level(round(row[1],3))
              level2 = which_level(round(row[2],3))
              print(row[0].strftime('%H:%M'), max(level1, level2) - min(level1, level2) )
              
        
def main(update_tickets=False):
    global count
    #date1 = dt.datetime.now().strftime('%Y-%m-%d')
    date1 = '2023-12-02' 
    if not os.path.exists(MAIN_DF_FILE):
       #tickets = get_tickets()
       tickets = ['PETR4', 'PETR3', 'BBDC4', 'BBDC3', 'GOAU4', 'GGBR4']
       df1 = pd.DataFrame({'Ativo' : tickets, 'Data/Hora' : dt.datetime.strptime(date1 + ' 18:00:00', '%Y-%m-%d %H:%M:%S')})
       df1.set_index('Data/Hora', inplace=True)
       df1 = update(df1)
       df1.dropna(inplace=True)
       df1.to_pickle(MAIN_DF_FILE)
       
    main_df = pd.read_pickle(MAIN_DF_FILE)
    main_df = main_df[main_df.index <= dt.datetime.strptime(date1, '%Y-%m-%d')]
    if update_tickets:
       main_df = update(main_df)
    main_df.dropna(inplace=True)
    #verify_trends(main_df)
    #correlation(main_df)
    #process_hits(main_df)
    #plot(['GOAU4','GGBR4'])
    #day_trade(['PETR4','PETR3'])
    long_short(main_df,['GOAU4', 'GGBR4'])
    
def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')           

warnings.simplefilter(action='ignore')
reset(reset_main=False)
main()
