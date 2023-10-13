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
FIRST_EMA_LEN = 10
SECOND_EMA_LEN = 30

def verify_trends(main_df):    
    if not main_df.empty:

        groups = main_df.groupby([pd.Grouper(freq='1d'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual', 'Financeiro']\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
           df_ticket = groups.loc[name][::-1]
           strategy(name, df_ticket)

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
            date = dt.datetime.strptime(row['Date'], '%Y-%m-%d')
            _data = {'Data/Hora' : date.strftime('%Y-%m-%d'), 'Ativo' : ticket, 'Variação' : '0,00%',\
                         'Máximo' : round(row['High'],2), 'Mínimo' : round(row['Low'],2) , 'Último' : round(row['Open'],2),\
                         'Abertura' : round(row['Open'],2), 'Financeiro' : row['Volume'], 'Estado Atual' : 'Aberto'}
            data.append(_data)            
   df4 =  pd.DataFrame(data)
   df4['Data/Hora'] = pd.to_datetime(df4['Data/Hora'])
   df4.set_index('Data/Hora', inplace=True)
   df4.sort_index(inplace=True)
   return df4      

def strategy(name, df_ticket):
  df_ticket.set_index('Data/Hora',inplace=True)
  df_ticket.sort_index(inplace=True)

  if name == 'IBOV':
     pass
  else:     
     df = df_ticket[['Último', 'Financeiro']]
     
     df['EMA_1'] = df['Último']['close'].ewm(span=FIRST_EMA_LEN, adjust=False).mean()
     df['EMA_2'] = df['Último']['close'].ewm(span=SECOND_EMA_LEN, adjust=False).mean()

     df = df[df.index >= dt.datetime.strftime(df.index[-1] - dt.timedelta(days = 120),'%Y-%m-%d')]
        
     if df[df['EMA_1'] > df['EMA_2']].empty:
        if df['Último']['close'][-1] >= df['EMA_1'][-1]:            
            print(name, 'Bearish', format_volume(df['Financeiro']['close'][-1]))      
           
     elif df[df['EMA_1'] < df['EMA_2']].empty:
         if df['Último']['close'][-1] <= df['EMA_1'][-1]:                
            print(name, 'Bullish', format_volume(df['Financeiro']['close'][-1]))

def get_tickets():
   data = []
   data.append('IBOV')
   with open("Tickets.txt") as file:
    for line in file:
        ticket = line.rstrip() 
        if '11' not in ticket:
           data.append(ticket)
   return data

def test(update_tickets=True):
    date1 = '2023-10-11'
    if not os.path.exists(MAIN_DF_FILE):
       tickets = get_tickets()
       df1 = pd.DataFrame({'Ativo' : tickets, 'Data/Hora' : dt.datetime.strptime(date1 + ' 18:00:00', '%Y-%m-%d %H:%M:%S')})
       df1.set_index('Data/Hora', inplace=True)
       df1 = update(df1)
       df1.dropna(inplace=True)
       df1.to_pickle(MAIN_DF_FILE, protocol=2)
       
    main_df = pd.read_pickle(MAIN_DF_FILE)
    main_df = main_df[main_df.index < dt.datetime.strptime(date1, '%Y-%m-%d')]
    if update_tickets:
       main_df = update(main_df)
    
    verify_trends(main_df)
        
        

def reset(reset_main):
   empty_json = {}
   if reset_main and os.path.exists(MAIN_DF_FILE):
      os.remove(MAIN_DF_FILE)   
   if reset_main and os.path.exists('stock_dfs'):
      shutil.rmtree('stock_dfs')           

warnings.simplefilter(action='ignore')
reset(reset_main=False)
test()
