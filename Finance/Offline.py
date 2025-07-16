import pandas as pd
import datetime as dt
from pymongo import MongoClient
import pdb
import time
import random
import numpy as np
import os

# 1️⃣ Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
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

    # 4️⃣ Upsert (insert or update) each row
    upserted_count = 0
    for _, row in df.iterrows():
        doc_time = dt.datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S')
        data = {
            "time": doc_time,
            "close": row['Close'],
            "volume": row['Volume'],
            "ativo": ticket,
            "open": row['Open'],
            "high": row['High'],
            "low": row['Low']
        }
        
        result = collection.update_one(
            {"time": doc_time},
            {"$set": data},
            upsert=True
        )
        if result.upserted_id or result.modified_count:
            upserted_count += 1

    print(f"{upserted_count} registros inseridos ou atualizados na coleção 'prices'.")


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





def simulate_daily_trading(date, rate=1, steps=5, prob_high_early=0.6, prob_bullish=0.55):
    # Load 5-minute OHLC data
    df = pd.read_csv('./stock_dfs/SBSP3.csv')
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df[df['Datetime'].dt.date == pd.to_datetime(date).date()]

    if df.empty:
        print(f"No data available for {date}")
        return

    for _, row in df.iterrows():
        timestamp = row['Datetime'].replace(second=0, microsecond=0)
        o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
        v = row['Volume']

        high_first = random.random() < prob_high_early
        is_bullish = c > o if random.random() < prob_bullish else c < o

        # Generate step path that includes the real high and low at random steps
        remaining_steps = steps - 3  # open, high, low, close are fixed
        mid_prices = []

        for _ in range(remaining_steps):
            mid = round(random.uniform(min(o, c), max(o, c)), 2)
            mid = max(min(mid, h), l)
            mid_prices.append(mid)

        # Randomly choose steps to insert the real high and low
        high_idx = random.randint(1, steps - 2)
        low_idx = random.randint(1, steps - 2)
        while low_idx == high_idx:
            low_idx = random.randint(1, steps - 2)

        # Build the full path
        path = [None] * steps
        path[0] = o
        path[-1] = c
        path[high_idx] = h
        path[low_idx] = l

        # Fill in midpoints
        mid_idx = 0
        for i in range(1, steps - 1):
            if path[i] is None:
                path[i] = mid_prices[mid_idx]
                mid_idx += 1

        print(f"\nSimulating candle @ {timestamp.time()} with {steps} steps")
        high_so_far = o
        low_so_far = o
        volume_so_far = 0

        for i in range(steps):
            price = path[i]
            high_so_far = max(high_so_far, price)
            low_so_far = min(low_so_far, price)
            volume_so_far += v / steps

            partial_candle = {
                "time": timestamp,
                "open": o,
                "high": round(high_so_far, 2),
                "low": round(low_so_far, 2),
                "close": round(price, 2),
                "volume": round(volume_so_far),
                "ativo": "SBSP3",
                "status": f"step_{i + 1}/{steps}"
            }

            collection.update_one(
                {"time": timestamp},
                {"$set": partial_candle},
                upsert=True
            )

            print(f" Step {i+1}: {price:.2f} (H: {high_so_far:.2f}, L: {low_so_far:.2f})")
            time.sleep(rate)

      
        final_candle = {
            "time": timestamp,
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": v,
            "ativo": "SBSP3",
            "status": "completed"
        }

        collection.update_one(
            {"time": timestamp},
            {"$set": final_candle}
        )

        print(f" Final candle saved @ {timestamp.time()}")

    print("\n Simulation completed for", date)


def update_with_fake_avg_values():


    for doc in collection.find():
        close_price = doc["close"]

        fake_buy_price = round(close_price - np.random.uniform(0.01, 0.10), 2)
        fake_sell_price = round(close_price + np.random.uniform(0.01, 0.10), 2)
        fake_buy_qty = int(np.random.randint(1000, 5000))
        fake_sell_qty = int(np.random.randint(1000, 5000))

        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "AvgBuyPrice": 0,
                    "AvgSellPrice": 0,
                    "AvgBuyQty": 0,
                    "AvgSellQty": 0
                }
            }
        )

    print("MongoDB documents updated with fake spread/imbalance values.")

def export_to_csv(input_date=None, output_path="./mongo_export.csv"):
    # Fetch all documents from the collection
    cursor = collection.find()
    data = list(cursor)

    if not data:
        print("No data found in MongoDB to export.")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    if input_date:
        df['time'] = pd.to_datetime(df['time'])  # Ensure 'time' is datetime
        df = df[df['time'].dt.date == pd.to_datetime(input_date).date()]

    # Drop Ativo column
    column_to_remove = "ativo"

    if column_to_remove in df.columns:
        df = df.drop(columns=[column_to_remove])


    # Drop MongoDB's internal _id field
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    # Drop columns with all NaN values
    df.dropna(axis=1, how='all', inplace=True)

    # Round all numeric columns to 2 decimal places
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} records to {output_path}")

def insert_from_uploaded_csv(file_path="mongo_export.csv"):
    try:
        df = pd.read_csv(file_path)
        if 'time' not in df.columns:
            print("Error: 'time' column not found in the CSV.")
            return

        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df.dropna(subset=['time'], inplace=True)

        # Convert DataFrame rows into dictionaries and upsert one-by-one
        inserted = 0
        for _, row in df.iterrows():
            record = row.to_dict()
            timestamp = record['time']
            del record['time']  # Remove 'time' from set to avoid overwrite conflicts

            result = collection.update_one(
                {'time': timestamp},
                {'$set': record, '$setOnInsert': {'time': timestamp}},
                upsert=True
            )
            if result.upserted_id or result.modified_count:
                inserted += 1

        print(f"Inserted/Updated {inserted} records from '{file_path}' into MongoDB.")
    except Exception as e:
        print(f"Failed to insert from CSV: {e}")


    

# Example usage:
#remove_registers_greater_than(dt.datetime(2025, 4, 6, 18, 00))
#erase_all_data()
#insert_data_from_csv()
#find_example_registers(10)
#simulate_daily_trading('2025-03-19', rate=0.5)
#update_with_fake_avg_values()
#export_to_csv('2025-06-06')
#insert_from_uploaded_csv()
#print(collection.index_information())

import json

# Step 1: Get all nQuoteNumbers (executed orders)
quote_numbers = set(db.times_trades.distinct("nQuoteNumber"))

# Step 2: Find one duplicated nCounterId that also appears in times_trades
pipeline = [
    {"$match": {"nCounterId": {"$in": list(quote_numbers)}}},
    {"$group": {"_id": "$nCounterId", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 1}
]
duplicate_doc = list(db.offer_book.aggregate(pipeline))

if not duplicate_doc:
    print("No matching duplicated nCounterId found that also exists in times_trades.")
    exit()

example_id = duplicate_doc[0]["_id"]
print(f"Analyzing nCounterId: {example_id} (Count: {duplicate_doc[0]['count']})")

# Step 3: Get all entries for that nCounterId
entries = list(db.offer_book.find({"nCounterId": example_id}, {"_id": 0}))

# Step 4: Convert datetime fields to strings for JSON serialization
def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(v) for v in obj]
    elif isinstance(obj, dt.datetime):
        return obj.isoformat()
    else:
        return obj

# Step 5: Remove exact duplicates using JSON and keep one per variant
normalized_entries = [convert_datetime(doc) for doc in entries]
unique_jsons = {json.dumps(doc, sort_keys=True) for doc in normalized_entries}
unique_docs = [json.loads(doc) for doc in unique_jsons]

# Step 6: Sort by time field (assumed ISO string format)
unique_docs_sorted = sorted(
    unique_docs,
    key=lambda x: dt.datetime.fromisoformat(x["time"]) if "time" in x else datetime.min
)

# Step 7: Print sorted results
print(f"\nFound {len(unique_docs_sorted)} distinct field combinations for nCounterId {example_id} (sorted by time):\n")
for i, doc in enumerate(unique_docs_sorted, 1):
    print(f"--- Variant {i} ---")
    for k, v in doc.items():
        print(f"{k}: {v}")
    print()








