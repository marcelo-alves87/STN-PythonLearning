import pymongo
from pymongo import MongoClient
import time
import datetime as dt
import pandas as pd
import pdb
import pickle
import winsound
import os
import shutil

dict = {}
    
def sound_alert():
   winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
   time.sleep(1)

def check_alert(ticket, df):
    if not df.empty:
        if (df['low'] == df['open'] and df['high'] > df['close'] and df['close'] > df['open']) or\
            (df['high'] == df['open'] and df['low'] < df['close'] and df['close'] < df['open']):
                print('{} at {}'.format(ticket, df.name))
                sound_alert()
        

while (True):
    if os.path.exists('main_df.pickle'):
       try:
          shutil.copyfile('main_df.pickle', 'main_df2.pickle')
          df = pd.read_pickle('main_df2.pickle')
       except:
          df = pd.DataFrame()
       if not df.empty and not 'Preço Teórico' in df.columns:
           df.reset_index(inplace=True)
           df = df[['Data/Hora', 'Ativo', 'Último']]
           if isinstance(df, pd.DataFrame):
               df.set_index('Data/Hora', inplace=True)
               df = df[df.index.date == dt.datetime.now().date()]
               groups = df.groupby([pd.Grouper(freq='5min'), 'Ativo'])\
                               .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
               groups.reset_index('Data/Hora',inplace=True)
               for name in groups.index.unique():
                   if name != 'IBOV':
                       df_ticket = groups.loc[name][::-1]
                       if not df_ticket.empty and isinstance(df_ticket, pd.DataFrame):
                           df_ticket.set_index('Data/Hora',inplace=True)
                           df_ticket.sort_index(inplace=True)                        
                           if len(df_ticket) > 1 and (name not in dict or dict[name] < df_ticket.index[-2]):
                               dict[name] = df_ticket.index[-2]
                               check_alert(name, df_ticket['Último'].iloc[-2])
    time.sleep(1)
        

