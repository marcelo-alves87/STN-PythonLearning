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

yfin.pdr_override()

MAIN_DF_FILE = 'main_df.pickle'
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
count_bull = 0
count_bear = 0
tickets_corr = []
CORR_THRESHOLD = 10

#fazer correlação com 30 min ou 15 min e verificar movimentos em 5-min

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
   start_date = actual_date - dt.timedelta(days=30)   
   end_date = actual_date + dt.timedelta(days=1)   
   # just in case your connection breaks, we'd like to save our progress!
   if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      try:
         ticket = format_ticket(ticket)
         print('{}'.format(ticket))
         df = web.get_data_yahoo(ticket + '.SA', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval = '5m')
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
     
     df_ticket = df_ticket[df_ticket.index >= dt.datetime.strftime(df_ticket.index[-1] - dt.timedelta(days = 6),'%Y-%m-%d')]

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
        date1 = df1.index[0]
        last_date = df1.index[-1]
        df1['EMA_1'] = df1['Último'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
        df1['EMA_2'] = df1['Último'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()


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
    #print_hit(df[df[2] > 4])
    pdb.set_trace()

def to_timezone(row):
    delta = 0
    if '-02:00' in row:
        delta = 1
    row = dt.datetime.strptime(row, '%Y-%m-%d %H:%M:%S%z')
    row -= dt.timedelta(hours=delta)   
    return row.strftime('%Y-%m-%d %H:%M:%S')

def plot(tickers):
    fig = mpf.figure(style='charles',figsize=(7,8))
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(3,1,3, sharex=ax1)

    for i in range(len(tickers)):
        if os.path.exists('stock_dfs/{}.csv'.format(tickers[i])):
         df = pd.read_csv('stock_dfs/{}.csv'.format(tickers[i]))
         df.reset_index(inplace=True)
         df['Datetime'] = df['Datetime'].apply(lambda row: to_timezone(row))
         
         df['EMA_1'] = df['Close'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
         df['EMA_2'] = df['Close'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

         df = df[df['Datetime'] > '2023-11-06']
         df = df[df['Datetime'] < '2023-11-07']
         
         #df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close','Volume']]
         df.index = pd.DatetimeIndex(df['Datetime'])
         

         if i == 0:
             apd_1 = mpf.make_addplot(df['EMA_1'],type='line', ax=ax1, color='blue')
             apd_2 = mpf.make_addplot(df['EMA_2'],type='line', ax=ax1, color='darkblue')
             mpf.plot(df,ax=ax1, ylabel=tickers[i], type='candle', addplot=[apd_1,apd_2])
         else:
             apd_1 = mpf.make_addplot(df['EMA_1'],type='line', ax=ax2, color='blue')
             apd_2 = mpf.make_addplot(df['EMA_2'],type='line', ax=ax2, color='darkblue')
             apd = mpf.make_addplot(df[['EMA_1', 'EMA_2']],type='line', ax=ax2)
             mpf.plot(df,ax=ax2,ylabel=tickers[i], type='candle',addplot=[apd_1,apd_2])
         

    mpf.show()

def main(update_tickets=False):
    global count
    date1 = '2023-11-08'
    if not os.path.exists(MAIN_DF_FILE):
       tickets = get_tickets()
       df1 = pd.DataFrame({'Ativo' : tickets, 'Data/Hora' : dt.datetime.strptime(date1 + ' 18:00:00', '%Y-%m-%d %H:%M:%S')})
       df1.set_index('Data/Hora', inplace=True)
       df1 = update(df1)
       df1.dropna(inplace=True)
       df1.to_pickle(MAIN_DF_FILE)
       
    main_df = pd.read_pickle(MAIN_DF_FILE)
    main_df = main_df[main_df.index < dt.datetime.strptime(date1, '%Y-%m-%d')]
    if update_tickets:
       main_df = update(main_df)
    main_df.dropna(inplace=True)
    #verify_trends(main_df)
    #correlation(main_df)
    process_hits(main_df)
    #plot(['MRFG3', 'B3SA3'])
    
    
def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')           

warnings.simplefilter(action='ignore')
reset(reset_main=False)
main()
