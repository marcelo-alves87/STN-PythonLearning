import os
import time
import datetime as dt
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from pymongo import MongoClient
import warnings
import shutil
import pdb

# Constants
URL = "https://rico.com.vc/"
PAUSE_FLAG_FILE = "pause.flag"
DB_CLIENT = MongoClient("localhost", 27017)
DB_PRICES = DB_CLIENT.mongodb.prices  # MongoDB collection for storing prices

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
        ["Ativo", "Último", "Financeiro", "Data/Hora"]
    ]
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"], dayfirst=True, errors="coerce")
    return df

def save_to_mongo(df):
    
    """Save the DataFrame to MongoDB, ensuring time index is included."""
    if df.index.name == "time":  # Only reset if 'time' is an index
        df = df.reset_index()

    records = df.to_dict("records")  # Convert to dictionary including the 'time' column
    result = DB_PRICES.insert_many(records)
    
    print(f"Data saved to MongoDB. Rows added: {len(result.inserted_ids)}")

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
    return value

def process_and_save_data(driver):
    """Process data and save it to MongoDB, ensuring correct format and ignoring IBOV."""
    df = scrape_tickets(driver)

    # Filter out rows where 'Ativo' is 'IBOV'
    df = df[df["Ativo"] != "IBOV"]

    if df.empty:
        print("No valid data to process after filtering out IBOV.")
        return

    # Convert "Último" (price) and "Financeiro" (volume) to numeric
    df["Último"] = df["Último"].apply(convert_numeric)
    df["Financeiro"] = df["Financeiro"].apply(convert_numeric)

    # Rename columns to match expected format
    df.rename(columns={
        "Ativo": "ativo",  # Fix Ativo -> ativo
        "Último": "close",
        "Financeiro": "volume",
        "Data/Hora": "time"
    }, inplace=True)

    # Ensure high, low, and open are the same as close
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["open"] = df["close"]

    df.set_index("time", inplace=True)

    # Get today's date in YYYY-MM-DD format
    today_str = dt.datetime.now().strftime("%Y-%m-%d")

    # Retrieve total accumulated volume per ativo for today
    total_volumes = {}
    pipeline = [
        {"$match": {"time": {"$gte": dt.datetime.strptime(today_str, "%Y-%m-%d")}}},  # Only today's records
        {"$group": {"_id": "$ativo", "total_volume": {"$sum": "$volume"}}}  # Sum all volumes per ativo
    ]
    existing_data = list(DB_PRICES.aggregate(pipeline))

    for entry in existing_data:
        total_volumes[entry["_id"]] = entry["total_volume"]  # Store accumulated volume per ativo

    # Calculate volume difference (If no previous volume for today, assume this is the first record)
    df["volume_diff"] = df.apply(lambda row: max(row["volume"] - total_volumes.get(row["ativo"], 0), 0), axis=1)

    # Use volume difference as the new volume value
    df["volume"] = df["volume_diff"]
    df.drop(columns=["volume_diff"], inplace=True)

    save_to_mongo(df)
 




def scrape_to_mongo():
    """Main method to scrape data and save to MongoDB."""
    driver = setup_scraper()

    while True:
        if os.path.exists(PAUSE_FLAG_FILE):
            print("Scraper paused. Waiting...")
            time.sleep(1)
            continue

        try:
            process_and_save_data(driver)
        except Exception as e:
            print(f"Error during scraping: {e}")
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
    """addPriceSerieEntityByDataSerieHistory"""
    """ mydata = t.filter((item) => item.dtDateTime >  new Date('2025-02-10'));"""
    """Scrape data and save it to CSV files."""
    driver = setup_scraper()
    try:
        main_df = scrape_tickets(driver)
        tickets = main_df["Ativo"].values
        ticket_count = len(tickets) - 1 if len(tickets) > 0 else 0
        print(f"Found {ticket_count} tickets to process.")

        for index, ticket in enumerate(tickets):
            if ticket != "IBOV":
                input('Waiting for mydata of {} ...'.format(ticket))
                length = driver.execute_script("return mydata.length")
                data = []

                for i in range(length):
                    date_str = driver.execute_script(f"return mydata[{i}].dtDateTime.toLocaleString()")
                    date = dt.datetime.strptime(date_str, "%d/%m/%Y, %H:%M:%S")
                    n_open = driver.execute_script(f"return mydata[{i}].nOpen")
                    
                    # Check for both possible property names using JavaScript fallback
                    n_max = driver.execute_script(
                        f"return mydata[{i}].nMax !== undefined ? mydata[{i}].nMax : mydata[{i}].nMaximum"
                    )
                    n_min = driver.execute_script(
                        f"return mydata[{i}].nMin !== undefined ? mydata[{i}].nMin : mydata[{i}].nMinimum"
                    )
                    n_close = driver.execute_script(f"return mydata[{i}].nClose")
                    n_volume = driver.execute_script(f"return mydata[{i}].nVolume")

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
        print("Scraping completed successfully.")
    finally:
        driver.quit()
        print("WebDriver closed. Script finished.")

if __name__ == "__main__":
    warnings.simplefilter(action="ignore")
    #get_data_to_csv()
    scrape_to_mongo()
