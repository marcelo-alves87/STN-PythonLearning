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
import traceback
from dateutil import parser
import re
from datetime import timedelta
import sys
import winsound  # works on Windows
import os
import ast  # safely evaluate list/number from file

# Constants
URL = "https://rico.com.vc/"
PAUSE_FLAG_FILE = "pause.flag"
DEBUG_FLAG_FILE = "debug.flag"
ALERT_FILE = "price_alert.txt"
DB_CLIENT = MongoClient("localhost", 27017)
DB_PRICES = DB_CLIENT.mongodb.prices  # MongoDB collection for storing aggregated prices
DB_SCRAPED_PRICES = DB_CLIENT.mongodb.scraped_prices
DB_OFFER_BOOK = DB_CLIENT.mongodb.offer_book
DB_TIMES_TRADES = DB_CLIENT.mongodb.times_trades
last_preco_teorico = None
last_status = None
last_qtd_teorica = None
volume_accumulated = 0
assistant_process = None

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
        time.sleep(5)
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
        ["Ativo", "Último", "Financeiro", "Data/Hora", "Estado Atual", "Preço Teórico", "Quantidade Teórica", "Variação Teórica"]
    ]
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"], dayfirst=True, errors="coerce")
    return df

def save_to_mongo(df):
    """Smart upsert to MongoDB: update OHLCV fields, preserve calculated ones like Absorption."""
    if df.index.name == "time":
        df = df.reset_index()

    records = df.to_dict("records")
    if not records:
        print("No records to save.")
        return

    times = [r["time"] for r in records]
    existing_docs = DB_PRICES.find({"time": {"$in": times}})
    existing_map = {doc["time"]: doc for doc in existing_docs}

    # Define which fields are directly updatable from source data
    updatable_fields = {
        "open", "high", "low", "close", "volume", "ativo", "time",
        "RawSpread_Mean", "DensitySpread_Mean", "Liquidity_Mean", "Pressure_Mean", "AgentImbalance_Max"
    }
    

    operations = []
    for record in records:
        time_value = record["time"]
        existing = existing_map.get(time_value, {})
        merged = existing.copy()

        for key in updatable_fields:
            if key in record:
                value = record[key]
                # Only update if new value is not null
                if value is not None and (not isinstance(value, float) or not math.isnan(value)):
                    merged[key] = record[key]

        operations.append(
            UpdateOne({"time": time_value}, {"$set": merged}, upsert=True)
        )

    if operations:
        result = DB_PRICES.bulk_write(operations)
        #print(f"Upserted: {result.upserted_count}, Modified: {result.modified_count}")

        


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

def compute_pressure(trades):
    """
    Compute normalized net pressure using bBuyerAggressor field.
    Pressure = (buy_qty - sell_qty) / total_qty
    Returns: float in range [-1, 1]
    """
    buy_qty = 0
    sell_qty = 0

    for t in trades:
        trade_type = t.get('nTradeType')
        if trade_type and trade_type != 4:
            qty = t.get("nQuantity") 
            is_buy_aggressor = t.get("bBuyerAgressor")

            if qty is None or is_buy_aggressor is None:
                continue

            if is_buy_aggressor:
                buy_qty += qty
            else:
                sell_qty += qty

    return buy_qty, sell_qty


# ---------- 1) SNAPSHOT: compute raw Support / Resistance (+ instantaneous Liquidity) ----------
def compute_liquidity_components(buy_book, sell_book, current_price):
    """
    Compute raw side scores at *this instant*:
      Support  = adaptive weighted score of buy_book
      Resistance = adaptive weighted score of sell_book
    Return (instant_liquidity, support, resistance) where:
      instant_liquidity = (Support - Resistance) / (Support + Resistance)  (0 if denom==0)
    """
    def _score(book, side):
        if not book:
            return 0.0
        # distances for scaling
        dists = []
        for lv in book:
            p = lv.get("price")
            if p is None: 
                continue
            try:
                dists.append(abs(float(p) - current_price))
            except (TypeError, ValueError):
                continue
        maxd = max(dists) if dists else 0.0
        if maxd == 0.0:
            maxd = 1.0  # avoid divide-by-zero; makes weights default to 1.0

        s = 0.0
        for lv in book:
            p = lv.get("price")
            q = lv.get("qty", lv.get("quantity", 0))
            try:
                p = float(p); q = float(q or 0)
            except (TypeError, ValueError):
                continue
            if q <= 0:
                continue
            d = p - current_price
            if side == "buy":
                w = max(0.0, 1.0 + (d / maxd))
            else:
                w = max(0.0, 1.0 - (d / maxd))
            s += q * w
        return float(s)

    if not buy_book or not sell_book:
        return 0, 0
    
    support    = _score(buy_book,  "buy")
    resistance = _score(sell_book, "sell")
    
    return support, resistance

def compute_density_components(buy_book, sell_book):
    """
    Return raw BuyDensity and SellDensity for the *current* snapshot.
    Density = sum(qty) / price_span (guarded against zero spans)
    """
    if not buy_book or not sell_book:
        return 0.0, 0.0

    buy_prices  = [e.get("price") for e in buy_book if e.get("price") is not None]
    sell_prices = [e.get("price") for e in sell_book if e.get("price") is not None]
    if not buy_prices or not sell_prices:
        return 0.0, 0.0

    buy_qty  = sum(float(e.get("qty", e.get("quantity", 0)) or 0) for e in buy_book)
    sell_qty = sum(float(e.get("qty", e.get("quantity", 0)) or 0) for e in sell_book)

    buy_span  = max(buy_prices)  - min(buy_prices)
    sell_span = max(sell_prices) - min(sell_prices)

    buy_den  = (buy_qty  / buy_span)  if buy_span  > 0 else 0.0
    sell_den = (sell_qty / sell_span) if sell_span > 0 else 0.0
    return buy_den, sell_den


def compute_raw_spread(buy_book, sell_book):

    if not buy_book or not sell_book:
        return 0
        
    best_bid = max(buy_book, key=lambda x: x["price"])['price']
    best_ask = min(sell_book, key=lambda x: x["price"])['price']

    return best_ask - best_bid

def save_into_scraped_prices(df):
    
    # 1. Assume df_scraped is already defined
    df_scraped = df[[
        "Data/Hora",
        "RawSpread",
        "BuyDensity",
        "SellDensity",
        "nQuoteNumber",
        "Support",
        "Resistance",
        "Pressure_BuyQty",
        "Pressure_SellQty",
        "BuyAgents",
        "SellAgents",
    ]].copy()

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

def save_offer_book(buy_book, sell_book, df):
    now = df['Data/Hora'].iloc[-1]
    current_price = df['Último'].iloc[-1]

    # Limit both books to top 20 levels
    top_buy_book = sorted(buy_book, key=lambda x: x["price"], reverse=True)[:20]
    top_sell_book = sorted(sell_book, key=lambda x: x["price"])[:20]

    # Clean and normalize fields
    def clean_book(book):
        return [
            {
                "price": level.get("price"),
                "quantity": level.get("qty") or level.get("quantity"),
                "count": level.get("count", 1),
                "nCounterId": level.get("nCounterId"),
                "agent": level.get("agent"),
            }
            for level in book
        ]

    snapshot = {
        "time": now,
        "current_price": current_price,
        "buy_book": clean_book(top_buy_book),
        "sell_book": clean_book(top_sell_book)
    }

    try:
        DB_OFFER_BOOK.insert_one(snapshot)
        # print(f"Saved book snapshot at {now.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Error saving offer book snapshot: {e}")


def save_times_trades_book(all_trades):
    try:
        DB_TIMES_TRADES.insert_many(all_trades)        
    except Exception as e:
        print(f"Error saving trades: {e}")

def compute_agent_imbalance(all_trades):
    """
    Snapshot Agent Imbalance from the just-scraped trades list.

    Returns a dict with:
      - AgentImbalance: normalized diff between (#buy_agents vs. #sell_agents)
      - AD_BuyAgents, AD_SellAgents: unique agent counts on each side
      - AD_BuyDict, AD_SellDict: dicts keyed by agent id with Σ(nQuoteNumber)
    Notes:
      * This is a per-snapshot measure. For exact 5-min values, recompute from DB in aggregation.
    """
    if not all_trades:
        return {
            "BuyAgents": 0,
            "SellAgents": 0,
        }

    df = pd.DataFrame(all_trades)

    # keep only normal on-book trade types if present
    if "nTradeType" in df.columns:
        df = df[df["nTradeType"].isin([2, 3])]

    # safe numeric casting
    for c in ["nQuoteNumber", "nBuyAgent", "nSellAgent"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # --- agent dictionaries (Σ of quotes per agent) ---
    buy_dict = (
        df.dropna(subset=["nBuyAgent", "nQuoteNumber"])
          .groupby("nBuyAgent")["nQuoteNumber"].sum()
          .astype(float).to_dict()
    )
    sell_dict = (
        df.dropna(subset=["nSellAgent", "nQuoteNumber"])
          .groupby("nSellAgent")["nQuoteNumber"].sum()
          .astype(float).to_dict()
    )

    # --- unique agent counts ---
    n_buy_agents  = int(df["nBuyAgent"].nunique(dropna=True)) if "nBuyAgent"  in df else 0
    n_sell_agents = int(df["nSellAgent"].nunique(dropna=True)) if "nSellAgent" in df else 0

    return {
        "BuyAgents": n_buy_agents,
        "SellAgents": n_sell_agents
    }

def print_auction_summary(all_trades):

    if not all_trades:
        return

    df = pd.DataFrame(all_trades)

    # Filter by TradeType == 4 (Auction trades)
    if "nTradeType" in df.columns:
        df = df[df["nTradeType"] == 4]
        if df.empty:
            return

    # Helper function to format numbers
    def human_format(num):
        for unit in ["", "k", "M", "B"]:
            if abs(num) < 1000.0:
                return f"{num:3.1f}{unit}"
            num /= 1000.0
        return f"{num:.1f}T"  # in case it reaches trillions

    buyer_agents = defaultdict(int)
    seller_agents = defaultdict(int)
    buy_vol = 0
    sell_vol = 0

    for trade in df.to_dict("records"):  # use filtered trades
        buyer_agents[trade["nBuyAgent"]] += 1
        seller_agents[trade["nSellAgent"]] += 1
        if trade.get("bBuyerAgressor"):            
            buy_vol += trade["nQuantity"] * trade['nPrice']
        else:
            sell_vol += trade["nQuantity"] * trade['nPrice']
            
            

    print("=== Post-Auction Summary ===")
    print(f"Number of Trades: {len(df)}")
    print(f"Number of Buyer Aggressors: {len(buyer_agents)}")
    print(f"Volume (Buy side): R$ {human_format(buy_vol)}")
    print(f"Number of Seller Aggressors: {len(seller_agents)}")
    print(f"Volume (Sell side): R$ {human_format(sell_vol)}")
    

def scrap_pricebook(driver, df):
    
    # JavaScript to scrape order book
    # Warning: These things can be asynchronous!
    js_price_book_buy = """return temp2.asset.offerBook.book.arrLimitedBuy.map(item => ({
        nCounterId: item.obj.nCounterID,
        price: item.obj.nPrice,
        qty: item.obj.nQty,
        agent: item.obj.nAgent,
        time: item.obj.dtDate.toString()
    }));"""

    js_price_book_sell = """return temp2.asset.offerBook.book.arrLimitedSell.map(item => ({
        nCounterId: item.obj.nCounterID,
        price: item.obj.nPrice,
        qty: item.obj.nQty,
        agent: item.obj.nAgent,
        time: item.obj.dtDate.toString()
    }));"""

    buy_book = driver.execute_script(js_price_book_buy)
    sell_book = driver.execute_script(js_price_book_sell)

    #save_offer_book(buy_book, sell_book, df)

    doc = DB_SCRAPED_PRICES.find_one(
        {"nQuoteNumber": {"$exists": True}},
        sort=[("nQuoteNumber", -1)]
    )
    last_quote_number = doc["nQuoteNumber"] if doc else -1

    today_str = dt.datetime.now().strftime("%Y-%m-%d")
    
    js_trades_script = f"""
    return temp2.asset.arrTrades
        .filter(entry => {{
            const quoteDate = new Date(entry.dtDate);
            const dateStr = quoteDate.toISOString().slice(0, 10);
            return entry.nQuoteNumber > {last_quote_number} && dateStr === "{today_str}";
        }})
        .map(entry => ({{
            dtDate: entry.dtDate.toString(),
            nPrice: entry.nPrice,
            nQuantity: entry.nQuantity,
            bBuyerAgressor: entry.bBuyerAgressor,
            nQuoteNumber: entry.nQuoteNumber,
            nBuyAgent: entry.nBuyAgent,
            nSellAgent: entry.nSellAgent,
            nTradeType: entry.nTradeType
        }}));
    """
    
    all_trades = driver.execute_script(js_trades_script)

    #save_times_trades_book(all_trades)

    print_auction_summary(all_trades)
    
    # 2. Compute raw spread
    spread = compute_raw_spread(buy_book, sell_book)    

    # 3. Compute DensitySpread
    bd, sd = compute_density_components(buy_book, sell_book)
    
    # 4. Compute Liquidity
    support, resistance = compute_liquidity_components(buy_book, sell_book, float(df['Último'].iloc[-1]))

    # 5. Compute Pressure
    press_buy, press_sell = compute_pressure(all_trades)

    # 6. Agent Density
    imbalance = compute_agent_imbalance(all_trades)
    

    # 5. Get the maximum nQuoteNumber from the list
    max_quote_number = max((t["nQuoteNumber"] for t in all_trades if "nQuoteNumber" in t), default=0)

    # 3. Save into latest row
    df.loc[df.index[-1], [
        "RawSpread",
        "nQuoteNumber",        
        "Pressure_BuyQty",     
        "Pressure_SellQty",
        "BuyAgents","SellAgents",
        "BuyDensity","SellDensity",
        "Support", "Resistance"
    ]] = [
        spread,
        max_quote_number,
        press_buy,
        press_sell,
        int(imbalance.get("BuyAgents", 0) or 0), int(imbalance.get("SellAgents", 0) or 0),
        bd, sd,
        support, resistance
    ]

    # Save result (your existing storage function)
    save_into_scraped_prices(df)

    return True

def tw_normalized_diff(df_snap: pd.DataFrame, pos_col: str, neg_col: str, freq="5T"):
    """
    Time-weighted normalized diff per bucket for two state variables.
    Treat each snapshot as piecewise-constant until the next one.
    """
    if df_snap.empty or not {pos_col, neg_col}.issubset(df_snap.columns):
        return pd.DataFrame(columns=["time", f"{pos_col}_TWMean", f"{neg_col}_TWMean", "NormDiff"]).set_index("time")

    df = df_snap[[pos_col, neg_col]].sort_index().copy()
    start = df.index[0].floor(freq)
    end   = df.index[-1].ceil(freq)
    buckets = pd.date_range(start, end, freq=freq)

    rows = []
    idx = df.index

    for B in buckets:
        B_end = B + pd.Timedelta(freq)

        # carry value at bucket start (last snapshot at or before B)
        i = idx.searchsorted(B, side="right") - 1
        times = []
        vals  = []
        if i >= 0:
            times.append(B)
            vals.append(df.iloc[i][[pos_col, neg_col]].values)

        # snapshots strictly inside (B, B_end)
        inner = df.loc[(idx > B) & (idx < B_end)]
        for t, r in inner.iterrows():
            times.append(t)
            vals.append(r[[pos_col, neg_col]].values)

        if not times:
            continue

        # integrate piecewise-constant until bucket end
        tw_pos = tw_neg = 0.0
        for j in range(len(times)):
            t0 = times[j]
            t1 = times[j+1] if j+1 < len(times) else B_end
            dt = (t1 - t0).total_seconds()
            if dt <= 0: 
                continue
            p, n = vals[j]
            tw_pos += float(p) * dt
            tw_neg += float(n) * dt

        total = (B_end - times[0]).total_seconds()
        if total <= 0:
            continue

        pos_mean = tw_pos / total
        neg_mean = tw_neg / total
        denom = pos_mean + neg_mean
        norm = 0.0 if denom == 0 else (pos_mean - neg_mean) / denom

        rows.append({"time": B,
                     f"{pos_col}_TWMean": pos_mean,
                     f"{neg_col}_TWMean": neg_mean,
                     "NormDiff": norm})

    return pd.DataFrame(rows).set_index("time").sort_index()

def price_alert(df):

    if os.path.exists(ALERT_FILE):

        last_price = float(df['Último'].iloc[-1])

        # Read target(s) from file
        with open(ALERT_FILE, "r") as f:
            content = f.read().strip()
        target = ast.literal_eval(content)  # safe parse into float or list

        triggered = False
        if isinstance(target, (list, tuple)) and len(target) == 2:
            low, high = min(target), max(target)
            if low <= last_price <= high:
                triggered = True
        else:
            if last_price == float(target):
                triggered = True

        if triggered:
            now = dt.datetime.today().strftime("%H:%M:%S")
            print(f"[{now}] 🔔 Price Alert! Last price {last_price} hit target {target}")
            # Play system exclamation sound
            if sys.platform.startswith("win"):
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            else:
                print("\a")  # bell for Linux/macOS

            # Rename file so it won't trigger again
            os.rename(ALERT_FILE, ALERT_FILE.replace(".txt", "_.txt"))

def process_and_save_data(driver):
    global last_preco_teorico, last_status, last_qtd_teorica, volume_accumulated
    """Process data, aggregate with previously saved records, and save to MongoDB."""
    df = scrape_tickets(driver)

    # Filter out rows where 'Ativo' is 'IBOV'
    df = df[df["Ativo"] != "IBOV"]
    
    if df.empty:
        print("No valid data to process.")
        return

    elif df.iloc[-1]["Estado Atual"] != "Aberto":
        status = df.iloc[-1]["Estado Atual"]
        df["Preço Teórico"] = df["Preço Teórico"].apply(convert_numeric)
        preco_teorico = df.iloc[-1]["Preço Teórico"]
        df["Quantidade Teórica"] = df["Quantidade Teórica"]
        qtd_teorica = df.iloc[-1]["Quantidade Teórica"]
        var_teorica = df.iloc[-1]["Variação Teórica"]
        now = dt.datetime.today().strftime("%H:%M:%S")

        if pd.notna(preco_teorico) and pd.notna(status) and pd.notna(qtd_teorica):
            if (
                last_preco_teorico is None 
                or last_status is None 
                or last_qtd_teorica is None
                or last_preco_teorico != preco_teorico 
                or last_status != status 
                or last_qtd_teorica != qtd_teorica
            ):
                print(f"({now}) {status}: {preco_teorico:.2f} | Qtde: {qtd_teorica} | Var: {var_teorica}")

            last_preco_teorico = preco_teorico
            last_status = status
            last_qtd_teorica = qtd_teorica
    else:
       
        # Reset Global Variables
        last_preco_teorico = None
        last_status = None        
        
        # Convert price and volume columns to numeric values
        df["Último"] = df["Último"].apply(convert_numeric)
        df["Financeiro"] = df["Financeiro"].apply(convert_numeric)

        try:
            price_alert(df)
        except:
            pass
        
        # Remove 'Estado Atual' and Preço Teórico columns
        df = df.drop(columns=["Estado Atual", "Preço Teórico"])
        
        try:
            scraped_pricebook_success = scrap_pricebook(driver, df)            
        except Exception as e:
            scraped_pricebook_success = False

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
            last_volumes = df_existing.groupby("ativo")["volume"].sum().to_dict()
            df["volume_raw"] = df["volume"]
            df["prev_volume"] = df["ativo"].map(last_volumes).fillna(0)
            df["volume"] = (df["volume_raw"] - df["prev_volume"]).apply(lambda x: x if x > 0 else 0)
            df.drop(columns=["prev_volume", "volume_raw"], inplace=True)

            df = pd.concat([df_existing, df])
        
        # Resample data to 5-minute intervals per 'ativo'
        df_resampled = df.groupby("ativo").resample("5T").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna().reset_index()        

        scraped_data = list(DB_SCRAPED_PRICES.find({"time": {"$gte": today_start}}, {"_id": 0}))
        df_scraped = pd.DataFrame(scraped_data)
        
        if scraped_pricebook_success and not df_scraped.empty:
            df_scraped["time"] = pd.to_datetime(df_scraped["time"])
            df_snap = df_scraped.set_index("time").sort_index()
            df_snap.drop(columns=["nQuoteNumber"], errors="ignore", inplace=True)

            # 5T resample for flows & pieces (no ratio means here)
            agg_map = {
                "RawSpread": "mean",
                "Pressure_BuyQty": "sum",
                "Pressure_SellQty": "sum",
                "BuyAgents": "max",   # snapshot approx for the union
                "SellAgents": "max",
            }
            use_map = {k: v for k, v in agg_map.items() if k in df_snap.columns}
            df5 = df_snap.resample("5T").agg(use_map)
            df5.index.name = "time"  # ensure a stable name for merge later

            # Pressure (compute once from totals)
            if {"Pressure_BuyQty", "Pressure_SellQty"}.issubset(df5.columns):
                B = df5.pop("Pressure_BuyQty").fillna(0.0).astype("float64")
                S = df5.pop("Pressure_SellQty").fillna(0.0).astype("float64")
                den = B + S
                pressure = pd.Series(0.0, index=df5.index, dtype="float64")
                m = den != 0
                pressure[m] = (B[m] - S[m]) / den[m]
                df5["Pressure_Mean"] = pressure

            ad_cols = {"BuyAgents", "SellAgents"}
            if ad_cols.issubset(df5.columns):
                NB = df5.pop("BuyAgents").fillna(0).astype("int64")
                NS = df5.pop("SellAgents").fillna(0).astype("int64")

                denom = NB + NS
                df5["AgentImbalance_Max"] = ((NB - NS).astype("float64") / denom.replace(0, numpy.nan)).fillna(0.0)



            # Liquidity (TIME-WEIGHTED from snapshots)
            if {"Support", "Resistance"}.issubset(df_snap.columns):
                tw_liq = tw_normalized_diff(df_snap, pos_col="Support", neg_col="Resistance", freq="5T")
                tw_liq.rename(columns={"NormDiff": "Liquidity_Mean"}, inplace=True)
                df5 = df5.merge(tw_liq[["Liquidity_Mean"]], left_index=True, right_index=True, how="left")

            # DensitySpread (TIME-WEIGHTED from snapshots)
            if {"BuyDensity", "SellDensity"}.issubset(df_snap.columns):
                tw_ds = tw_normalized_diff(df_snap, pos_col="BuyDensity", neg_col="SellDensity", freq="5T")
                tw_ds.rename(columns={"NormDiff": "DensitySpread_Mean"}, inplace=True)
                df5 = df5.merge(tw_ds[["DensitySpread_Mean"]], left_index=True, right_index=True, how="left")

            # Rename any remaining simple means
            df5.rename(columns={"RawSpread": "RawSpread_Mean"}, inplace=True)

            df5 = df5.reset_index()  # 'time' stays as a column thanks to index.name set above
            df_resampled = pd.merge(df_resampled, df5, on="time", how="left")


         


        # Save the newly aggregated data
        save_to_mongo(df_resampled)


def handle_exception(error=None, shutdown=True):
    global assistant_process
    if error:
        print("Traceback (most recent call last):")
        traceback.print_tb(error.__traceback__)  # Prints the stack trace
    if shutdown:       
        try:
            if assistant_process and assistant_process.poll() is None:
                assistant_process.terminate()
                print("LiveTradeAssistant process terminated.")
            driver.quit()
            print("Selenium driver closed.")
        except Exception as e:
            print(f"Error closing driver: {e}")



def scrape_to_mongo():
    input("Remember to store 'this' of const e = this.asset.arrTrades as the global variable temp2 ...")

    show_message = True

    try:
        while True:
            try:
                if os.path.exists(PAUSE_FLAG_FILE):
                    if not show_message:
                        print("Scraper paused. Waiting...")
                        show_message = True
                    time.sleep(1)
                    continue

                if show_message:
                    print("Running scraper ...")
                    print("Stop its execution typing CTRL + C ...")
                    show_message = False

                if os.path.exists(DEBUG_FLAG_FILE):
                    pdb.set_trace()

                process_and_save_data(driver)
                time.sleep(1)

            except Exception as e:
                handle_exception(e, False)
                time.sleep(2)  # Optional: wait before retrying to avoid hammering

    except KeyboardInterrupt:
        handle_exception()
        print("Scraper stopped by user.")


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

                if not df.empty:
                    print(f"Last time getted: {df['Datetime'].iloc[-1]}")

                #Remove pos-market data
                df = df[
                    (df["Datetime"].dt.time <= dt.time(16, 50)) &
                    (df["Datetime"].dt.time != dt.time(0, 0))
                ]

                if not df.empty:
                    print(f"Getting data until: {df['Datetime'].iloc[-1]}")

                    # Make python max and min price from last day  <-- added
                    last_day = df["Datetime"].dt.date.iloc[-1]
                    df_last_day = df[df["Datetime"].dt.date == last_day]

                    max_price = df_last_day["High"].max()
                    min_price = df_last_day["Low"].min()
                    print(f"Max price on {last_day}: {max_price}")
                    print(f"Min price on {last_day}: {min_price}")
 
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
    DB_OFFER_BOOK.delete_many({})
    DB_TIMES_TRADES.delete_many({})

if __name__ == "__main__":
    warnings.simplefilter(action="ignore")
    delete_scraped_collection()
    driver = setup_scraper()
    get_data_to_csv()
    scrape_to_mongo()
    driver.quit()
