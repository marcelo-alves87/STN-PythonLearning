import pymongo
from pymongo import MongoClient
import time
import datetime as dt
import pandas as pd
import pdb

client =  MongoClient("localhost", 27017)
db = client["mongodb"]
prices = db["prices"]


def reset_data():
   prices.delete_many({})   

def insert_data(ticket, date):
   data = []
   df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
   df1['Datetime'] = pd.to_datetime(df1['Datetime'])
   df1 = df1[df1['Datetime'].dt.date <= pd.to_datetime(date).date()]
   for i,row in df1.iterrows():
      dt1 = {"time": dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S'),\
            "close": row['Close'], "volume": row['Volume'], "ativo": ticket,\
            "open" : row['Open'], "high" : row['High'], "low" : row['Low']}
      data.append(dt1)
   prices.insert_many(data)

def insert_document(ticket, date, sleep):
    data = []
    df1 = pd.read_csv('stock_dfs/{}.csv'.format(ticket))
    df1['Datetime'] = pd.to_datetime(df1['Datetime'])
    df1 = df1[df1['Datetime'].dt.date == pd.to_datetime(date).date()]
    for i,row in df1.iterrows():
      dt1 = {"time": dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S'),\
            "close": row['Close'], "volume": row['Volume'], "ativo": ticket,\
            "open" : row['Open'], "high" : row['High'], "low" : row['Low']}
      prices.insert_one(dt1)
      time.sleep(sleep)
      
#reset_data()
#insert_data('VIVT3', '2024-03-12')
insert_document('VIVT3', '2024-03-13', 5)


#insert_document('ARZZ3','2024-03-19 17:46:00', 64.01, 267529999)


#prices.insert_one(data)
#for dt in prices.find():
#    print(dt)
#print(db.prices.count_documents({}))
#prices.delete_many({})
#print(prices.find_one())

#print(list(prices.find().sort({'time':1}).limit(1)))

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
