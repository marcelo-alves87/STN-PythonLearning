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
PRICE_ALERT = 'Price_Alert.txt'
THRESHOLD = 0.98
last_lvl = {}
price_alert = {}
succeeded = []
all = []
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
           
           if name not in last_lvl and df_ticket['Mínimo']['open'][-1] > df_ticket['Mínimo']['low'][-1] \
              and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
              last_lvl[name] = [df_ticket['Máximo']['high'][-1], 'Bearish'] 
              notify(df_ticket.index[-1], name, 'Short', df_ticket['Máximo']['high'][-1], df_ticket['Mínimo']['open'][-1],\
                     df_ticket['Variação']['close'][-1], main_df[main_df['Ativo'] == name]['Financeiro'][-2])
           elif name in last_lvl and last_lvl[name][1] == 'Bearish' and df_ticket['Último']['close'][-2] > last_lvl[name][0]:
              last_lvl.pop(name)

           if name not in last_lvl and df_ticket['Máximo']['open'][-1] < df_ticket['Máximo']['high'][-1] \
              and df_ticket['Mínimo']['low'][-1]/df_ticket['Máximo']['high'][-1] < THRESHOLD:
              last_lvl[name] = [df_ticket['Mínimo']['low'][-1], 'Bullish']
              notify(df_ticket.index[-1], name, 'Long', df_ticket['Máximo']['open'][-1], df_ticket['Mínimo']['low'][-1],\
                     df_ticket['Variação']['close'][-1], main_df[main_df['Ativo'] == name]['Financeiro'][-2])
           elif name in last_lvl and last_lvl[name][1] == 'Bullish' and df_ticket['Último']['close'][-2] < last_lvl[name][0]:
              last_lvl.pop(name)

           if name in price_alert and df_ticket['Último']['high'][-1] >= price_alert[name] \
              and df_ticket['Último']['low'][-1] <= price_alert[name]:              
              print(df_ticket.index[-1], name)            
              price_alert.pop(name) 
              succeeded.append(name)
              
def get_status(variation):
   variation = variation.replace('%','')
   variation = variation.replace(',','.')
   return float(variation)

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
   print(index,'********',name, '********', type, lvl0, lvl100, round(lvl100/lvl0,2), variation, round(finance/1000, 2), cal_gross_value(type, lvl0, lvl100))
   all.append(name)
   if type == 'Short':
      target = lvl100 - (lvl0 - lvl100)      
   else:
      target = lvl0 + (lvl0 - lvl100)

   price_alert[name] = target  
      
def handle_finance(row):   
   if isinstance(row, float):
      return row
   else:
      row = row.replace('.','')
      row = row.replace(',','')
      row = row[:-3] + '.' + row[-3:]
      if 'k' in row:
         row = float(row.replace('k',''))
         row = row * 10**3
      elif 'M' in row:
         row = float(row.replace('M',''))
         row = row * 10**6
      elif 'B' in row:
         row = float(row.replace('B',''))
         row = row * 10**9   
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
print(len(all))
print(len(succeeded))
print(succeeded)
print(100 * len(succeeded)/len(all))
