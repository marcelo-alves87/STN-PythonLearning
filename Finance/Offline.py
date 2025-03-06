import pandas as pd
import datetime as dt
from pymongo import MongoClient
import pdb
import time

# 1️⃣ Connect to MongoDB
client = MongoClient("localhost", 27017)
db = client["mongodb"]  # Database name
collection = db["prices"]  # Collection name

def insert_data_from_csv(date=None):
    # 2️⃣ Load the CSV file
    csv_file_path = "./stock_dfs/SBSP3.csv"
    df = pd.read_csv(csv_file_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors='coerce')
    if date:
        date = pd.to_datetime(date).date()        
        df = df[df['Datetime'].dt.date <= date]

    # 3️⃣ Define the stock ticker
    ticket = "SBSP3"

    # 4️⃣ Convert DataFrame to MongoDB format
    data_list = []
    for _, row in df.iterrows():
        data = {
            "time": dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S'),
            "close": row['Close'],
            "volume": row['Volume'],
            "ativo": ticket,
            "open": row['Open'],
            "high": row['High'],
            "low": row['Low']
        }
        data_list.append(data)

    # 5️⃣ Insert into MongoDB
    if data_list:
        collection.insert_many(data_list)
        print(f"Inserted {len(data_list)} records into MongoDB collection 'prices'.")
    else:
        print("No data found in CSV to insert.")

# 6️⃣ Method to erase all data from the collection
def erase_all_data():
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} records from the collection.")

# 7️⃣ Method to remove records greater than a timestamp
def remove_registers_greater_than(timestamp):
    result = collection.delete_many({"time": {"$gt": timestamp}})
    print(f"Deleted {result.deleted_count} records with time greater than {timestamp}.")

# 8️⃣ Method to find and display records from the database
def find_example_registers(size=1):
    results = collection.find().sort("time", -1).limit(size)  # Replace "time" with your actual timestamp field name
    if results:
        print(f"Last {size} Registers Found:")
        for example in results:
            print(example)
    else:
        print("No records found in the database.")





def simulate_daily_trading(date, rate=1):
    csv_file_path = "./stock_dfs/SBSP3_1min.csv"
    df = pd.read_csv(csv_file_path)

    # Ensure 'Datetime' is in datetime format
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    date = pd.to_datetime(date).date()  # Ensure date format  

    # Filter data for the selected date
    df = df[df['Datetime'].dt.date == date]

    if df.empty:
        print(f"No data available for {date}")
        return

    # Process 1-minute data row-by-row and update 5-minute candles dynamically
    for _, row in df.iterrows():
        timestamp_1min = dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S')

        # Convert 1-minute timestamp to its corresponding 5-minute bucket
        timestamp_5min = timestamp_1min.replace(minute=(timestamp_1min.minute // 5) * 5, second=0)

        # Retrieve the existing 5-minute candle
        existing_candle = collection.find_one({"time": timestamp_5min})

        if existing_candle:
            # If a 5-min candle exists, update it dynamically
            updated_candle = {
                "time": timestamp_5min,
                "open": existing_candle["open"],  # Keep the original open price
                "high": max(existing_candle["high"], row['High']),  # Update high
                "low": min(existing_candle["low"], row['Low']),  # Update low
                "close": row['Close'],  # Update close as the latest value
                "volume": existing_candle["volume"] + row['Volume'],  # Accumulate volume
                "ativo": "SBSP3"
            }
            collection.update_one({"time": timestamp_5min}, {"$set": updated_candle})
        else:
            #  If no existing candle, create a new one
            new_candle = {
                "time": timestamp_5min,
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": row['Volume'],
                "ativo": "SBSP3"
            }
            collection.insert_one(new_candle)

        # Sleep to simulate real-time data flow
        time.sleep(rate)

    print(f"Simulation for {date} completed with proper 5-minute candle updates.")



    

# Example usage:
#remove_registers_greater_than(dt.datetime(2025, 2, 27, 17, 50))
#erase_all_data()
#insert_data_from_csv('2025-02-26')
#find_example_registers(10)
simulate_daily_trading('2025-02-27',3)



