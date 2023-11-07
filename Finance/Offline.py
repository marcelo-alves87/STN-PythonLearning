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

yfin.pdr_override()

MAIN_DF_FILE = 'main_df.pickle'
DATA_FILE = 'data.pickle'
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30
count_bull = 0
count_bear = 0
tickets_corr = []

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
   start_date = actual_date - dt.timedelta(days=200)   
   end_date = actual_date + dt.timedelta(days=1)   
   # just in case your connection breaks, we'd like to save our progress!
   if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
      try:
         ticket = format_ticket(ticket)
         print('{}'.format(ticket))
         df = web.get_data_yahoo(ticket + '.SA', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
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
            date = dt.datetime.strptime(row['Datetime'][:-6], '%Y-%m-%d %H:%M:%S')
            _data = {'Data/Hora' : date.strftime('%Y-%m-%d %H:%M:%S'), 'Ativo' : ticket, 'Variação' : '0,00%',\
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
   data.append('IBOV')
   with open("Tickets.txt") as file:
    for line in file:
        ticket = line.rstrip() 
        if '11' not in ticket:
           data.append(ticket)
   return data

def remove(list, item):
    try:
        list.remove(item)
    except:
        pass

def process_data_corr(main_df):
    data = {}
    tickers = main_df['Ativo']
    tickers.drop_duplicates(inplace=True)
    
    for i,ticker in tickers.items():
        
        date1 = main_df.index[0]
        last_date = main_df.index[-1]
        bullish = []
        bearish = []

        df2 = main_df[main_df['Ativo'] == ticker]
        df2 = df2[df2.index > df2.index[-1].strftime('%Y-%m-%d')]
        volume = (df2['Financeiro'] * df2['Último']).sum()
        if has_great_volume(volume):
            while date1 < last_date:

                df1 = main_df[main_df['Ativo'] == ticker]
                date1_str = dt.datetime.strftime(date1,'%Y-%m-%d')
                if date1_str not in data:
                    data[date1_str] = {}
                
                df1['EMA_1'] = df1['Último'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
                df1['EMA_2'] = df1['Último'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

                df1 = df1[df1.index > date1]
                df1 = df1[df1.index < date1 + dt.timedelta(days = 1)]

                #processa os dados de hoje junto com os dados de ontem
                if ticker in bullish and not df1[df1['EMA_1'] < df1['EMA_2']].empty:
                    first_index = df1[df1['EMA_1'] < df1['EMA_2']].index[0]
                    index_str = dt.datetime.strftime(first_index,'%H:%M:%S')
                    if index_str in data[date1_str]:
                        data[date1_str][index_str] += [ticker, 'Bearish']
                    else:
                        data[date1_str][index_str] = [ticker, 'Bearish']                
                   
                elif ticker in bearish and not df1[df1['EMA_1'] > df1['EMA_2']].empty:
                    first_index = df1[df1['EMA_1'] > df1['EMA_2']].index[0]
                    index_str = dt.datetime.strftime(first_index,'%H:%M:%S')
                    if index_str in data[date1_str]:
                        data[date1_str][index_str] += [ticker, 'Bullish']
                    else:
                        data[date1_str][index_str] = [ticker, 'Bullish']                
                   

                remove(bullish,ticker)
                remove(bearish,ticker)
                    
                # armazena dados de hoje
                if df1[df1['EMA_1'] > df1['EMA_2']].empty:
                    bearish.append(ticker)                
                elif df1[df1['EMA_1'] < df1['EMA_2']].empty:
                    bullish.append(ticker)
                    
                date1 += dt.timedelta(days = 1)
    return data    

def main(update_tickets=False):
    global count
    date1 = '2023-11-01'
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

    if os.path.exists(DATA_FILE):
        df  = pd.read_pickle(DATA_FILE)
    else:    
        data = process_data_corr(main_df)         
        df = pd.DataFrame(data)
        df.sort_index(inplace=True)
        df.to_pickle(DATA_FILE)
        
    for column in range(len(df.columns)):
        print('-------------')
        print(df.columns[column])
        print('-------------')
        for i,row in df.iterrows():
           if isinstance(row[column], list):
               print(i,row[column])
            
def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)
   if reset_main and os.path.exists(DATA_FILE):
      os.remove(DATA_FILE)      
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')           

warnings.simplefilter(action='ignore')
reset(reset_main=False)
main()
