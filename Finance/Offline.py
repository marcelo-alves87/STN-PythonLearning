import pymongo
from pymongo import MongoClient
import time
import datetime as dt
import pandas as pd
import pdb
import os
import yfinance as yfin
import pandas_datareader.data as web
from threading import Thread

yfin.pdr_override()

client =  MongoClient("localhost", 27017)
db = client["mongodb"]
prices = db["prices"]
tickets = ['SBSP3', 'VALE3', 'SUZB3', 'BBAS3', 'ARZZ3', 'RENT3']

def get_data_from_yahoo(start_date, end_date):
   global tickets
   if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')
   for ticket in tickets:   
      # just in case your connection breaks, we'd like to save our progress!
      if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
         
         print('{}'.format(ticket))
         df = web.get_data_yahoo(ticket + '.SA', start=start_date, end=end_date, interval="1m")
         if not df.empty:
            df.reset_index(inplace=True)
            df['Datetime'] = df['Datetime'].astype(str)
            df['Datetime'] = df['Datetime'].apply(lambda row : row.replace('-03:00',''))
            df['Open'] = df['Open'].apply(lambda row : round(float(row),2))
            df['High'] = df['High'].apply(lambda row : round(float(row),2))
            df['Low'] = df['Low'].apply(lambda row : round(float(row),2))
            df['Close'] = df['Close'].apply(lambda row : round(float(row),2))
            df['Adj Close'] = df['Adj Close'].apply(lambda row : round(float(row),2))            
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df.to_csv('stock_dfs/{}.csv'.format(ticket))           
      
      
      
def reset_data():
   prices.delete_many({})

def resample(ticket, df1):
   data = []
   df1.set_index('Datetime', inplace=True)
   groups = df1.groupby([pd.Grouper(freq='5min')])\
                    .agg([('open','first'),('high', 'max'),('low','min'),('close','last')])
   groups.reset_index('Datetime',inplace=True)
   groups.dropna(inplace=True)
   for i,row in groups.iterrows():      
      dt1 = {"Datetime": dt.datetime.strptime(str(row['Datetime'][0]), '%Y-%m-%d %H:%M:%S'),\
            "Close": row['Close']['close'], "Volume": row['Volume']['close'],\
            "Open" : row['Open']['open'], "High" : row['High']['high'], "Low" : row['Low']['low']}
      data.append(dt1)
   return pd.DataFrame(data)
   
def insert_data(ticket, date, shift=0, resample_=False):
   data = []
   df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
   df1['Datetime'] = pd.to_datetime(df1['Datetime'])
   df1 = df1[df1['Datetime'].dt.date <= pd.to_datetime(date).date()]
   df1['Datetime'] += dt.timedelta(days=shift)
   if resample_:
      df1 = resample(ticket, df1)
   for i,row in df1.iterrows():
      dt1 = {"time": dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S'),\
            "close": row['Close'], "volume": row['Volume'], "ativo": ticket,\
            "open" : row['Open'], "high" : row['High'], "low" : row['Low']}
      data.append(dt1)
   prices.insert_many(data)

def insert_document(ticket, date, sleep, resample_=False, shift=0):
    data = []
    df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
    df1['Datetime'] = pd.to_datetime(df1['Datetime'])
    df1 = df1[df1['Datetime'].dt.date == pd.to_datetime(date).date()]
    df1['Datetime'] += dt.timedelta(days=shift)
    if resample_:
       df1 = resample(ticket, df1)
    for i,row in df1.iterrows():
      date = dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S')
      dt1 = {"time": date,\
            "close": row['Close'], "volume": row['Volume'], "ativo": ticket,\
            "open" : row['Open'], "high" : row['High'], "low" : row['Low']}
      prices.insert_one(dt1)
      time.sleep(sleep)

get_data_from_yahoo('2024-04-04', '2024-04-11')
#reset_data()
#for ticket in tickets:      
#   insert_data(ticket, '2024-04-11')
#   time.sleep(.5)
#for ticket in tickets:      
#   for i in range(1,5):
#      insert_data(ticket, '2024-04-09', -i, True)
#      time.sleep(.5)

#for i in range(len(tickets)):
#   input('Next {} ...'.format(tickets[i]))
#   insert_document(tickets[i], '2024-04-09', 7, True, 0)
   

#for ticket in tickets:
#    t = Thread(target=insert_document, args=(ticket, '2024-04-04', 2.5, False, 0))
#    t.start()

#insert_document('RENT3', '2024-03-26', 2.5)
#insert_document('ARZZ3','2024-03-19 17:46:00', 64.01, 267529999)


#prices.insert_one(data)
#for dt in prices.find():
#    print(dt)
#print(db.prices.count_documents({}))
#prices.delete_many({})
#print(prices.find_one())

#print(list(prices.find({'ativo' : 'BBAS3', 'time' : { '$gt' : dt.datetime.strptime("2024-03-27 11:11:00", '%Y-%m-%d %H:%M:%S')}}).sort({'time':1}).limit(1)))

#s = "01/12/2011"
#time1 = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
#print(int(time1))
#

#data = {"time": dt.datetime.strptime("2024-03-14 13:51:59", '%Y-%m-%d %H:%M:%S'), \
#        "close": 60.64, "volume": 267529999.99999997, "ativo": "VALE3" ,\
#        "open" : 60.64, "high" : 60.64, "low" : 60.64}
        
#prices.insert_one(data)

#data = [{"time": dt.datetime.strptime("2024-03-14 13:52:09", '%Y-%m-%d %H:%M:%S'), \
#        "close": 60.85, "volume": 267529999.99999997, "ativo": "VALE3" ,\
#        "open" : 60.64, "high" : 60.64, "low" : 60.64},\
#        {"time": dt.datetime.strptime("2024-03-14 13:51:03", '%Y-%m-%d %H:%M:%S'), \
#        "close": 60.59, "volume": 267529999.99999997, "ativo": "VALE3" ,\
#        "open" : 60.59, "high" : 60.59, "low" : 60.59}]
#prices.insert_many(data)


#prices.delete_many({'time': { '$gt' :  dt.datetime.strptime("2024-03-13 18:00:00", '%Y-%m-%d %H:%M:%S')}})

#print(list(prices.find({'ativo' : 'ELET6'}).sort({'time':1}).limit(1)))


