import os
import time
import datetime as dt
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from pymongo import MongoClient
from pymongo import UpdateOne
import warnings
import shutil
import pdb
import numpy
from collections import defaultdict
import math

# Constants
URL = "https://rico.com.vc/"
PAUSE_FLAG_FILE = "pause.flag"
DB_CLIENT = MongoClient("localhost", 27017)
DB_PRICES = DB_CLIENT.mongodb.prices  # MongoDB collection for storing aggregated prices
DB_SCRAPED_PRICES = DB_CLIENT.mongodb.scraped_prices # MongoDB collection for storing scraped prices
last_preco_teorico = None
last_status = None
volume_accumulated = 0

# Global persistent cluster trackers
buy_cluster_tracker = defaultdict(int)
sell_cluster_tracker = defaultdict(int)


def switch_to_correct_tab(driver):
    """Switch to the tab containing the desired element."""
    tabs_size = len(driver.window_handles)
    for i in range(tabs_size):
        driver.switch_to.window(driver.window_handles[i])
        try:
            # Try to find and click the 'app-menu' element
            driver.execute_script("document.getElementById('app-menu').click()")
            print("Switched to the correct tab.")
            break
        except:
            pass
    else:
        print("Unable to locate the correct tab. Please check manually.")
        
def get_page_source(driver):
    """Retrieve the page source with retry mechanism."""
    try:
        return driver.page_source
    except WebDriverException:
        time.sleep(1)
        return get_page_source(driver)

def get_page_df(driver):
    """Extract table data from the page into a DataFrame."""
    html = get_page_source(driver)
    soup = BeautifulSoup(html, features="lxml")
    tables = soup.find_all("table", class_="nelo-table-group")
    return pd.read_html(str(tables[0]))[0]

def setup_scraper():
    """Set up Selenium WebDriver and navigate to the target URL."""
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    input("Waiting for user login...")
    switch_to_correct_tab(driver)  # Ensure the correct tab is active
    print("Running scraping...")
    return driver

def scrape_tickets(driver):
    """Scrape ticket data from the webpage and return as a DataFrame."""
    df = get_page_df(driver)
    df = df[
        ["Ativo", "Último", "Financeiro", "Data/Hora", "Estado Atual", "Preço Teórico"]
    ]
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"], dayfirst=True, errors="coerce")
    return df

def save_to_mongo(df):
    """Efficiently upsert DataFrame rows into MongoDB, preserving existing fields."""
    if df.index.name == "time":
        df = df.reset_index()

    records = df.to_dict("records")
    if not records:
        print("No records to save.")
        return

    # Step 1: Get all times in the incoming data
    times = [r["time"] for r in records]

    # Step 2: Fetch existing docs in one query
    existing_docs = DB_PRICES.find({"time": {"$in": times}})
    existing_map = {doc["time"]: doc for doc in existing_docs}

    # Step 3: Prepare bulk upserts
    operations = []
    for record in records:
        time_value = record["time"]
        existing = existing_map.get(time_value)
        if existing:
            merged = existing.copy()
            merged.update(record)
            operations.append(
                UpdateOne({"_id": existing["_id"]}, {"$set": merged})
            )
        else:
            operations.append(
                UpdateOne({"time": time_value}, {"$set": record}, upsert=True)
            )

    # Step 4: Execute bulk write
    if operations:
        result = DB_PRICES.bulk_write(operations)
        


def convert_numeric(value):
    """Convert values from string format to numeric format."""
    if isinstance(value, str):
        value = value.replace(".", "").replace(",", ".")
        if value.endswith("k"):
            return float(value[:-1]) * 1e3
        elif value.endswith("M"):
            return float(value[:-1]) * 1e6
        elif value.endswith("B"):
            return float(value[:-1]) * 1e9
        elif len(value) > 2:
            return float(value[:-2] + '.' + value[-2:])
        else:
            return float(value)
    elif isinstance(value, (numpy.int64, int)):
        return float(value / 1e2)
    else:   
        return value

def save_into_scraped_prices(df):

    # 1. Assume df_scraped is already defined
    df_scraped = df[['Data/Hora', 'OrderBookScore', 'Spread']].copy()

    # 2. Rename column and convert to datetime
    df_scraped.rename(columns={'Data/Hora': 'time'}, inplace=True)
    df_scraped['time'] = pd.to_datetime(df_scraped['time'])

    DB_SCRAPED_PRICES.create_index('time', unique=True)

    # 5. Prepare bulk upsert operations to avoid duplicates
    operations = [
        UpdateOne(
            {'time': row['time']},
            {'$set': row},
            upsert=True
        )
        for row in df_scraped.to_dict(orient='records')
    ]

    # 6. Execute the bulk write
    if operations:
        result = DB_SCRAPED_PRICES.bulk_write(operations)

def update_persistent_clusters(buy_book, sell_book, current_price,
                                quantity_threshold=1500, distance_limit=0.15,
                                tracker_buy=None, tracker_sell=None):
    for level in buy_book:
        price = level["price"]
        qty = level["quantity"]
        if price < current_price and qty >= quantity_threshold and (current_price - price) <= distance_limit:
            tracker_buy[price] += 1

    for level in sell_book:
        price = level["price"]
        qty = level["quantity"]
        if price > current_price and qty >= quantity_threshold and (price - current_price) <= distance_limit:
            tracker_sell[price] += 1

def compute_proximity_score_from_clusters(current_price,
                                          buy_cluster_tracker,
                                          sell_cluster_tracker,
                                          buy_book,
                                          sell_book,
                                          max_distance=0.15):
    """
    Calculates a score from -100 (resistance) to +100 (support)
    based on proximity to persistent clusters.
    """
    support_score = 0
    resistance_score = 0
    best_bid = max(buy_book, key=lambda x: x["price"])['price']
    best_ask = min(sell_book, key=lambda x: x["price"])['price']
    spread = best_ask - best_bid

    for price, hits in buy_cluster_tracker.items():
        dist = current_price - price
        if 0 < dist <= max_distance:
            support_score += hits / dist

    for price, hits in sell_cluster_tracker.items():
        dist = price - current_price
        if 0 < dist <= max_distance:
            resistance_score += hits / dist

    total = support_score + resistance_score
    if total == 0:
        return 0, spread

    return 100 * (support_score - resistance_score) / total, spread

def scrap_pricebook(driver, df):
    # JavaScript to scrape order book
    js_price_book_buy = """return temp2.priceBook.arrPriceBookOriginal.buy.map(entry => ({
        price: entry.nPrice,
        quantity: entry.nQuantity,
        count: entry.nCount
    }));"""

    js_price_book_sell = """return temp2.priceBook.arrPriceBookOriginal.sell.map(entry => ({
        price: entry.nPrice,
        quantity: entry.nQuantity,
        count: entry.nCount
    }));"""

    buy_book = driver.execute_script(js_price_book_buy)
    sell_book = driver.execute_script(js_price_book_sell)

    if not buy_book or not sell_book:
        return

    current_price = df["Último"].iloc[-1]

    # 1. Track persistent clusters
    update_persistent_clusters(
        buy_book,
        sell_book,
        current_price,
        quantity_threshold=1500,
        distance_limit=0.15,
        tracker_buy=buy_cluster_tracker,
        tracker_sell=sell_cluster_tracker
    )

    # 2. Compute proximity score
    proximity_score, spread = compute_proximity_score_from_clusters(
        current_price,
        buy_cluster_tracker,
        sell_cluster_tracker,
        buy_book,
        sell_book,
        max_distance=0.15        
    )

    # 3. Save into latest row
    df.at[df.index[-1], "OrderBookScore"] = proximity_score
    df.at[df.index[-1], "Spread"] = spread    

    # Save result (your existing storage function)
    save_into_scraped_prices(df)
  

def process_and_save_data(driver):
    global last_preco_teorico, last_status, volume_accumulated 
    """Process data, aggregate with previously saved records, and save to MongoDB."""
    df = scrape_tickets(driver)

    # Filter out rows where 'Ativo' is 'IBOV'
    df = df[df["Ativo"] != "IBOV"]
    
    if df.empty:
        print("No valid data to process.")
        return

    elif "Aberto" != df.iloc[-1]["Estado Atual"]:        
        
        status = df.iloc[-1]["Estado Atual"]
        df["Preço Teórico"] = df["Preço Teórico"].apply(convert_numeric)
        preco_teorico = df.iloc[-1]["Preço Teórico"]
        now = dt.datetime.today().strftime("%H:%M:%S")
             
        if last_preco_teorico is None or last_status is None or last_preco_teorico != preco_teorico or last_status != status:
            print(f"({now}) {status}: {preco_teorico:.2f}")
               
        last_preco_teorico = preco_teorico
        last_status = status
            
    else:

        
        
        # Reset Global Variables
        last_preco_teorico = None
        last_status = None
        
        # Convert price and volume columns to numeric values
        df["Último"] = df["Último"].apply(convert_numeric)
        df["Financeiro"] = df["Financeiro"].apply(convert_numeric)

        # Remove 'Estado Atual' and Preço Teórico columns
        df = df.drop(columns=["Estado Atual", "Preço Teórico"])

        scrap_pricebook(driver, df)

        # Rename columns to match the database format
        df.rename(columns={
            "Ativo": "ativo",
            "Último": "close",
            "Financeiro": "volume",
            "Data/Hora": "time"
        }, inplace=True)

        # Ensure high, low, and open are initialized as the close price
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["open"] = df["close"]

        # Set time as the index
        df.set_index("time", inplace=True)

        # Get today's date
        today_start = dt.datetime.combine(dt.datetime.today(), dt.time(0, 0))       

        # Retrieve existing data from MongoDB for the current day
        existing_data = list(DB_PRICES.find({"time": {"$gte": today_start}}, {"_id": 0}))
        df_existing = pd.DataFrame(existing_data)        

        # Append new data to the existing one
        if not df_existing.empty:
            df_existing = df_existing.set_index('time')
            # Get the last stored volume for each `ativo`
            last_volumes = df_existing.groupby("ativo")["volume"].sum().to_dict()
            
            # Map stored volume to the new scraped data
            df["prev_volume"] = df["ativo"].map(last_volumes).fillna(0)

            # Compute volume difference per `ativo`
            df["volume"] = (df["volume"] - df["prev_volume"]).clip(lower=0)
            
            
            # Drop temporary column
            df.drop(columns=["prev_volume"], inplace=True)

            df = pd.concat([df_existing, df])
        
        # Resample data to 5-minute intervals per 'ativo'
        df_resampled = df.groupby("ativo").resample("5T").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "last"
        }).dropna().reset_index()

        # Remove previous data from MongoDB that falls within the resampled time range
        min_time = df_resampled["time"].min()
        max_time = df_resampled["time"].max()
        
        DB_PRICES.delete_many({"time": {"$gte": min_time, "$lte": max_time}})

        scraped_data = list(DB_SCRAPED_PRICES.find({"time": {"$gte": today_start}}, {"_id": 0}))
        df_scraped = pd.DataFrame(scraped_data)
        if not df_scraped.empty:
            df_scraped["time"] = pd.to_datetime(df_scraped["time"])
            df_scraped.set_index("time", inplace=True)

            df_scraped_ohlc = df_scraped.resample("5T").agg({
                "OrderBookScore": ["first", "max", "min", "mean"],
                "Spread": ["first", "max", "min", "mean"] 
            })

            # Rename columns to _Open, _High, _Low, _Close
            df_scraped_ohlc.columns = [
                "OrderBookScore_Open", "OrderBookScore_High", "OrderBookScore_Low", "OrderBookScore_Close",
                "Spread_Open", "Spread_High", "Spread_Low", "Spread_Close"
            ]

            df_scraped_ohlc.reset_index(inplace=True)            

            df_resampled = pd.merge(df_resampled, df_scraped_ohlc, on="time", how="left")

            

        # Save the newly aggregated data
        save_to_mongo(df_resampled)



def scrape_to_mongo():

    input("Remember to store 'this' inside getPriceBook() as the global variable temp2 ...")
    show_message = True
    while True:
        if os.path.exists(PAUSE_FLAG_FILE):
            if show_message is False:
                print("Scraper paused. Waiting...")
                show_message = True
            time.sleep(1)            
            continue

        try:
            if show_message:
                print("Running scraper ...")
                show_message = False
            process_and_save_data(driver)
        except Exception as e:
            #print(f"Error during scraping: {e}")
            time.sleep(5)

        time.sleep(1)

def save_csv_data():
    """Save data from CSV files to MongoDB."""
    df = pd.DataFrame()
    if os.path.exists("stock_dfs"):
        for file_name in os.listdir("stock_dfs"):
            file_path = os.path.join("stock_dfs", file_name)
            df1 = pd.read_csv(file_path)
            df1["ativo"] = file_name.replace(".csv", "")
            df1["Datetime"] = pd.to_datetime(df1["Datetime"])
            df1.rename(
                columns={
                    "Datetime": "time",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                },
                inplace=True,
            )
            df = pd.concat([df, df1])
        save_to_mongo(df)

def get_data_to_csv():   
    
    """Scrape data and save it to CSV files."""
    print("Remember to store the 't' parameter from addPriceSerieEntityByDataSerieHistory as the global variable temp1 ...")
    try:
        main_df = scrape_tickets(driver)
        tickets = main_df["Ativo"].values
        ticket_count = len(tickets) - 1 if len(tickets) > 0 else 0
        print(f"Found {ticket_count} tickets to process.")

        for index, ticket in enumerate(tickets):
            if ticket != "IBOV":
                
                input('Waiting for temp1 to point to {} ...'.format(ticket))
                length = driver.execute_script("return temp1.length")
                data = []

                for i in range(length):
                    date_str = driver.execute_script(f"return temp1[{i}].dtDateTime.toLocaleString()")
                    date = dt.datetime.strptime(date_str, "%d/%m/%Y, %H:%M:%S")
                    n_open = driver.execute_script(f"return temp1[{i}].nOpen")
                    
                    # Check for both possible property names using JavaScript fallback
                    n_max = driver.execute_script(
                        f"return temp1[{i}].nMax !== undefined ? temp1[{i}].nMax : temp1[{i}].nMaximum"
                    )
                    n_min = driver.execute_script(
                        f"return temp1[{i}].nMin !== undefined ? temp1[{i}].nMin : temp1[{i}].nMinimum"
                    )
                    n_close = driver.execute_script(f"return temp1[{i}].nClose")
                    n_volume = driver.execute_script(f"return temp1[{i}].nVolume")

                    data.append(
                        {
                            "Datetime": date,
                            "Open": n_open,
                            "High": n_max,
                            "Low": n_min,
                            "Close": n_close,
                            "Volume": n_volume,
                        }
                    )
                    print(f"Scraping [{i + 1}/{length}] data for {ticket}...")
                df = pd.DataFrame(data)
                df["Datetime"] = df["Datetime"] - dt.timedelta(hours=3)

                #Remove pos-market data
                df = df[df["Datetime"].dt.time <= dt.time(17, 50)]
 
                folder_path = "stock_dfs"
                os.makedirs(folder_path, exist_ok=True)
                file_path = f"{folder_path}/{ticket}.csv"

                if os.path.exists(file_path):
                    existing_df = pd.read_csv(file_path)
                    existing_df["Datetime"] = pd.to_datetime(existing_df["Datetime"])
                    df = pd.concat([existing_df, df]).drop_duplicates(subset=["Datetime"]).sort_values(by="Datetime").reset_index(drop=True)                   
                    print(f"Data appended to {file_path}.")
                else:
                    print(f"New file created: {file_path}.")

                # Save to CSV 
                df.to_csv(file_path, index=False)
                print(f"Data for ticket {ticket} saved to {file_path}.")
        
        save_csv_data()        
    finally:        
        print("Scraping of last prices completed.")

def delete_scraped_collection():
    DB_SCRAPED_PRICES.delete_many({})

if __name__ == "__main__":
    warnings.simplefilter(action="ignore")
    delete_scraped_collection()
    driver = setup_scraper()
    get_data_to_csv()
    scrape_to_mongo()
    driver.quit()
