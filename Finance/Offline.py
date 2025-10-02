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



def export_data_to_csv():    

    # Format volume with k, M, B
    def format_volume(value):
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}k"
        return str(value)

    # Fetch and process documents
    records = []
    for doc in collection.find():
        record = {}
        # Format time
        if "time" in doc:
            if isinstance(doc["time"], dt.datetime):
                record["time"] = doc["time"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                record["time"] = dt.datetime.strptime(str(doc["time"]), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

        for key, value in doc.items():
            if key in ["_id", "ativo", "time"]:
                continue
            if isinstance(value, (int, float)):
                if key == "volume":
                    record[key] = format_volume(value)
                else:
                    record[key] = round(value, 2)
        records.append(record)

    # Convert to DataFrame and export
    df = pd.DataFrame(records)
    df.to_csv("exported_prices.csv", index=False)
    print("CSV export completed.")


#Helper methods

# Parse volume with suffixes
def _parse_volume(v):
    if pd.isna(v):
        return None
    if isinstance(v, (int, np.integer)):
        return int(v)
    s = str(v).strip().lower().replace(",", "")
    mult = 1
    if s.endswith("k"):
        mult = 1_000
        s = s[:-1]
    elif s.endswith("m"):
        mult = 1_000_000
        s = s[:-1]
    elif s.endswith("b"):
        mult = 1_000_000_000
        s = s[:-1]
    try:
        return int(round(float(s) * mult))
    except Exception:
        return None


def insert_data_from_exported_csv(date=None,csv_file_path="exported_prices.csv", ticket="SBSP3"):
    """
    Insert/upsert documents from an `exported_prices.csv` file back into the
    MongoDB `prices` collection.

    - Expects a `time` column in the format YYYY-MM-DD HH:MM:SS.
    - Ensures Volume is stored as an integer, parsing suffixes like k/M/B.
    - Includes extended metrics if present: AgentImbalance_Max, DensitySpread_Mean,
      Liquidity_Mean, Pressure_Mean, RawSpread_Mean.

    Args:
        csv_file_path (str): Path to exported_prices.csv
        ticket (str): Ticker symbol to set in the `ativo` field (default 'SBSP3')
    """

    if not os.path.exists(csv_file_path):
        print(f"CSV not found: {csv_file_path}")
        return

    df = pd.read_csv(csv_file_path)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    if "time" not in df.columns:
        print("CSV does not contain a 'time' column.")
        return
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    if date:
        date = pd.to_datetime(date).date()
        df = df[df['time'].dt.date < date]

        # Make python max and min price from last day  <-- added
        last_day = df["time"].dt.date.iloc[-1]
        df_last_day = df[df["time"].dt.date == last_day]

        max_price = df_last_day["high"].max()
        min_price = df_last_day["low"].min()
        print(f"Max price on {last_day}: {max_price}")
        print(f"Min price on {last_day}: {min_price}")
    
    df = df.dropna(subset=["time"]).copy()

    if "volume" in df.columns:
        df["volume"] = df["volume"].apply(_parse_volume)
    else:
        df["volume"] = None

    numeric_fields = [
        "open", "high", "low", "close", "AgentImbalance_Max",
        "DensitySpread_Mean", "Liquidity_Mean", "Pressure_Mean", "RawSpread_Mean"
    ]
    for col in numeric_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    upserted_count = 0
    
    for _, row in df.iterrows():
        doc_time = row["time"]
        data = {"time": doc_time, "ativo": ticket}

        # Assign fields if present
        for col in numeric_fields + ["volume"]:
            if col in df.columns and not pd.isna(row.get(col)):
                if col == "volume":
                    data["volume"] = int(row[col]) if row[col] is not None else None
                else:
                    data[col] = float(row[col])

        result = collection.update_one(
            {"time": doc_time},
            {"$set": data},
            upsert=True,
        )
        if result.upserted_id or result.modified_count:
            upserted_count += 1

    print(f"{upserted_count} registros inseridos/atualizados a partir de '{csv_file_path}'.")


def simulate_daily_trade(date, csv_file_path="exported_prices.csv", ticket="SBSP3", sleep=0):
    """
    Simulate intraday trading by inserting one candle at a time from a CSV for a specific date.
    Pressing Enter inserts the next candle into MongoDB.
    """
    erase_all_data()

    insert_data_from_exported_csv(date=date, csv_file_path=csv_file_path, ticket=ticket)

    # Load the entire CSV
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return

    df = pd.read_csv(csv_file_path)
    df.columns = [c.strip() for c in df.columns]

    if "time" not in df.columns:
        print("CSV does not contain a 'time' column.")
        return

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    date_obj = pd.to_datetime(date).date()
    df = df[df["time"].dt.date == date_obj]
    df = df.sort_values("time")
    
    if df.empty:
        print(f"No candles found for date: {date}")
        return

    # Parse volume
    if "volume" in df.columns:
        df["volume"] = df["volume"].apply(_parse_volume)
    else:
        df["volume"] = None

    numeric_fields = [
        "open", "high", "low", "close", "AgentImbalance_Max",
        "DensitySpread_Mean", "Liquidity_Mean", "Pressure_Mean", "RawSpread_Mean"
    ]
    for col in numeric_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"Ready to simulate {len(df)} candles for {date}. Press Enter to insert each one.")

    auto_continue = False

    for idx, row in df.iterrows():
        if not auto_continue:
            user_input = input(f"\n[{row['time']}] Press Enter to insert next candle or 'C' to continue automatically: ").strip().lower()
            if user_input == 'c':
                auto_continue = True

        doc_time = row["time"]
        data = {"time": doc_time, "ativo": ticket}

        for col in numeric_fields + ["volume"]:
            if col in df.columns and not pd.isna(row.get(col)):
                if col == "volume":
                    data["volume"] = int(row[col]) if row[col] is not None else None
                else:
                    data[col] = float(row[col])

        result = collection.update_one(
            {"time": doc_time},
            {"$set": data},
            upsert=True,
        )

        print(f"Inserted candle @ {doc_time.strftime('%H:%M')} with Close={data.get('close')}, Volume={data.get('volume')}")

        if auto_continue:
            time.sleep(sleep)

    print("✅ Simulation completed.")


def remove_midnight_records():

    # Get all distinct dates in the collection
    all_dates = collection.distinct("time")
    
    for date in all_dates:
        # Convert to datetime if it's a string
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        
        # Build midnight datetime for that day
        midnight = date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Delete the midnight record if exists
        result = collection.delete_one({"time": midnight})
        
        if result.deleted_count > 0:
            print(f"Removed midnight record for {midnight.date()}")

    

# Example usage:
#remove_registers_greater_than(dt.datetime(2025, 4, 6, 18, 00))
#erase_all_data()
#insert_data_from_csv()
#find_example_registers(10)
#export_data_to_csv()
insert_data_from_exported_csv()
#simulate_daily_trade('2025-09-15', sleep=2)
#remove_midnight_records()



