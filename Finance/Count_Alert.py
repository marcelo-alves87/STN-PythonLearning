import pandas as pd
import pdb
import time
import datetime as dt
import os
import json
import sys
import pickle
import warnings



MAIN_DF_FILE = 'main_df.pickle'
THRESHOLD = 0.98
last_lvl = {}
INVESTMENT = 200

def verify_trends(main_df):
    
    if not main_df.empty:
        
        groups = main_df.groupby([pd.Grouper(freq='5min'), 'Ativo'])['Último', 'Máximo', 'Mínimo', 'Variação', 'Estado Atual'].agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
        groups.reset_index('Data/Hora',inplace=True)
        for name in groups.index.unique():
         df_ticket = groups.loc[name][::-1]
         
         if isinstance(df_ticket, pd.DataFrame) and len(df_ticket.index) > 2:
           
           df_ticket.set_index('Data/Hora',inplace=True)
           df_ticket.sort_index(inplace=True)
           
           if name not in last_lvl and df_ticket['Mínimo']['low'][-2] > df_ticket['Mínimo']['low'][-1] \
              and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
              last_lvl[name] = [df_ticket['Máximo']['high'][-1], 'Bearish'] 
              notify(df_ticket.index[-1], name, 'Short', df_ticket['Máximo']['high'][-1], df_ticket['Mínimo']['open'][-1],\
                     df_ticket['Variação']['close'][-1], main_df[main_df['Ativo'] == name]['Financeiro'][-2])
           elif name in last_lvl and last_lvl[name][1] == 'Bearish' and df_ticket['Último']['close'][-2] > last_lvl[name][0]:
              print(df_ticket.index[-1], name, 'Bearish Reversing') 
              last_lvl.pop(name)

           if name not in last_lvl and df_ticket['Máximo']['high'][-2] < df_ticket['Máximo']['high'][-1] \
              and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
              last_lvl[name] = [df_ticket['Mínimo']['low'][-1], 'Bullish']
              notify(df_ticket.index[-1], name, 'Long', df_ticket['Máximo']['open'][-1], df_ticket['Mínimo']['low'][-1],\
                     df_ticket['Variação']['close'][-1], main_df[main_df['Ativo'] == name]['Financeiro'][-2])
           elif name in last_lvl and last_lvl[name][1] == 'Bullish' and df_ticket['Último']['close'][-2] < last_lvl[name][0]:
              print(df_ticket.index[-1], name, 'Bull Reversing')  
              last_lvl.pop(name)

                  
def get_status(variation):
   variation = variation.replace('%','')
   variation = variation.replace(',','.')
   variation = float(variation)
   if variation > 0:
      return [1,variation]
   elif variation < 0:
      return [-1,variation]
   else:
      return [0,variation]

def cal_gross_value(type, lvl0, lvl100):
   if type == 'Short':
      lvlx = lvl100 - (lvl0 - lvl100)
      price = lvl100
   else:
      lvlx = lvl0 + (lvl0 - lvl100)
      price = lvl0
         
   leverage = INVESTMENT * 100
   volume = int(leverage/price)

   if type == 'Short':
      gross_value = (price - lvlx) * volume
   else:
      gross_value = (lvlx - price) * volume
   return round(gross_value,2)

def notify(index, name, type, lvl0, lvl100, variation, finance, ignore_restrictions=False):
   var = get_status(variation)
   if ((var[0] == 1 and type == 'Short') or (var[0] == -1 and type == 'Long'))\
        or (var[0] == 1 and var[1] > 2.85 and var[1] < 4):       
       print(index,'********',name, '********', type, lvl0, lvl100, round(lvl100/lvl0,2), variation, finance , cal_gross_value(type, lvl0, lvl100))   
       
def handle_finance(row):   
   if isinstance(row, float):
       row = round(row,2)
       if row > 10 ** 9:
           row = row / 10 ** 9 
           row = '{} B'.format(row)
       elif row > 10 ** 6:
           row = row / 10 ** 6 
           row = '{} M'.format(row)
       elif row > 10 ** 3:
           row = row / 10 ** 3
           row = '{} k'.format(row)
        
   return row
   

def test():
    
    main_df = pd.read_pickle(MAIN_DF_FILE)
    time1 = main_df.index[0]
    last_time = main_df.index[-1]
    
    while time1 < last_time:

        df = main_df.reset_index()
        df = df[df['Data/Hora'] < time1]        
        df['Financeiro'] = df['Financeiro'].apply(lambda row : handle_finance(row)) 
        
        df.set_index('Data/Hora', inplace=True)
        df.sort_index(inplace=True)
         
        verify_trends(df)

        #time.sleep(1)
        time1 += dt.timedelta(minutes = 5)

         
warnings.simplefilter(action='ignore', category=FutureWarning)
test()

