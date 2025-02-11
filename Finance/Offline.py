import pandas as pd
import datetime as dt
from pymongo import MongoClient

# 1️⃣ Connect to MongoDB
client = MongoClient("localhost", 27017)
db = client["mongodb"]  # Database name
collection = db["prices"]  # Collection name

def insert_data_from_csv():
    # 2️⃣ Load the CSV file
    csv_file_path = "./stock_dfs/SBSP3.csv"
    df = pd.read_csv(csv_file_path)

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

# 8️⃣ Method to find and display one example record from the database
def find_example_register():
    example = collection.find_one()
    if example:
        print("Example Register Found:")
        print(example)
    else:
        print("No records found in the database.")

# Example usage:
# erase_all_data()
#remove_registers_greater_than(dt.datetime(2025, 2, 5, 17, 50))
#find_example_register()

erase_all_data()
insert_data_from_csv()
