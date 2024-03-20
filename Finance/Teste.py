import pymongo
from pymongo import MongoClient
import time
import datetime as dt

client =  MongoClient("localhost", 27017)
db = client["mongodb"]
prices = db["prices"]

#prices.insert_one(data)
#for dt in prices.find():
#    print(dt)
#print(db.prices.count_documents({}))
#prices.delete_many({})
#print(prices.find_one())

print(list(prices.find().sort({'time':1}).limit(1)))

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
