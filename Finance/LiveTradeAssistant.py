from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import pdb
import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Graceful exit handler
def cleanup_and_exit(signum=None, frame=None):
    print("\n🔻 Gracefully shutting down...")
    try:
        driver.quit()
        print("✅ Selenium driver closed.")
    except Exception as e:
        print(f"⚠️ Failed to close driver: {e}")
    sys.exit(0)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
collection = client["mongodb"]["prices"]

# Get dynamic first candle time
today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

while True:
    cursor = collection.find({"time": {"$gt": today_start}}).sort("time", 1).limit(1)
    first_doc = next(cursor, None)
    if not first_doc:
        time.sleep(30)
        #print(f"❌ No trading data found for today (starting from {today_start}).")
        continue
    else:
        break
FIRST_CANDLE = str(first_doc["time"])
TODAY = FIRST_CANDLE[:10]  # yyyy-mm-dd

# Selenium setup
chrome_options = Options()
chrome_options.binary_location = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
chrome_options.add_argument(r"--user-data-dir=C:\\ChromeSession")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://chat.openai.com")

last_checked_time = None
entry_defined = False

# ChatGPT interaction

def wait_for_stable_response(timeout=30, stable_duration=1.0):
    wait = WebDriverWait(driver, timeout)
    container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown.prose")))
    previous_text, stable_start = None, None

    while True:
        messages = driver.find_elements(By.CSS_SELECTOR, "div.markdown.prose")
        if not messages:
            time.sleep(0.2)
            continue
        latest = messages[-1].text.strip()

        if latest == previous_text:
            if stable_start is None:
                stable_start = time.time()
            elif latest and len(latest) > 0 and time.time() - stable_start >= stable_duration:
                break
        else:
            previous_text = latest
            stable_start = None
        time.sleep(0.2)

    return latest

def send_prompt_to_chatgpt(prompt):
    try:
        wait = WebDriverWait(driver, 20)
        textarea = wait.until(EC.presence_of_element_located((By.ID, "prompt-textarea")))
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.ENTER)
        return wait_for_stable_response()
    except Exception as e:
        return f"⚠️ Error: {e}"

def get_latest_data():
    return collection.find().sort("time", -1).limit(1)[0]

def format_candle_line(doc):
    ts = pd.to_datetime(doc["time"]).strftime("%Y-%m-%d %H:%M:%S")
    close = doc["close"]
    high = doc["high"]
    low = doc["low"]
    open_ = doc["open"]
    volume = doc["volume"]
    density = doc.get("DensitySpread_Mean", "")
    rawspread = doc.get("RawSpread_Mean", "")
    liquidity = doc.get("Liquidity_Mean", "")
    pressure = doc.get("Pressure_Mean", "")

    header = (
        "| time | close | high | low | open | volume | Density | RawSpread | Liquidity | Pressure |"
    )
    values = (
        f"| {ts} | {close} | {high} | {low} | {open_} | {volume} | "
        f"{density} | {rawspread} | {liquidity} | {pressure} |"
    )
    return f"{header} {values}"

import textwrap

def print_output(response, wrap_width=100):
    now = datetime.now().strftime('%H:%M')
    raw_lines = response.strip().split('\n')
    
    # Wrap long lines
    wrapped_lines = []
    for line in raw_lines:
        wrapped_lines.extend(textwrap.wrap(line, width=wrap_width) or [""])

    width = max(len(line) for line in wrapped_lines + [f" {now} "])
    border = '+' + '-' * (width + 2) + '+'

    print(border)
    print(f"| {now.ljust(width)} |")
    print(border)
    for line in wrapped_lines:
        print(f"| {line.ljust(width)} |")
    print(border + '\n', flush=True)



def run_analysis():
    global last_checked_time, entry_defined

    while True:
        if not last_checked_time:
            # Get all candles from previous trading day for context            
            FIRST_CANDLE_DT = datetime.strptime(FIRST_CANDLE, "%Y-%m-%d %H:%M:%S")
            last_day = collection.find({"time": {"$lt": FIRST_CANDLE_DT}}).sort("time", -1).limit(1)[0]["time"].strftime("%Y-%m-%d")
            start_prev_day = pd.to_datetime(last_day)
            end_prev_day = start_prev_day + pd.Timedelta(days=1)
            prev_docs = list(collection.find({
                "time": {
                    "$gte": start_prev_day,
                    "$lt": end_prev_day
                }
            }).sort("time", 1))            
            # Extract OHLC from previous day
            if prev_docs:
                open_prev_day = prev_docs[0]["open"]
                close_prev_day = prev_docs[-1]["close"]
                high_prev_day = max(doc["high"] for doc in prev_docs)
                low_prev_day = min(doc["low"] for doc in prev_docs)
            else:
                open_prev_day = close_prev_day = high_prev_day = low_prev_day = "N/A"
            
            # Format as inline readable summary
            prev_day_ohlc_line = (
                f"(Prev Day OHLC - Open: {open_prev_day}, High: {high_prev_day}, "
                f"Low: {low_prev_day}, Close: {close_prev_day})"
            )
            curr_line = format_candle_line(first_doc)
            timestamp = datetime.now().strftime("%H:%M:%S")

            prompt = (
                f"Now it's {timestamp}. Please analyze the first 5-minute candle from {TODAY} using the previous trading day's data and give me only the conclusion. "
                f"Remember, the candle might not be closing yet."
                f"Here is the previous trading day data summary: "
                f"{prev_day_ohlc_line}"
                f"Here is the first candle of the day: "
                f"{curr_line}"
            )
            
            response = send_prompt_to_chatgpt(prompt)
            print_output(response)
            last_checked_time = str(first_doc["time"])
        else:
            time.sleep(60)
            now = datetime.now().strftime('%H:%M')
            latest = get_latest_data()
            latest_line = format_candle_line(latest)
            prompt = (
                f"Continue analyzing this 5-minute candle in context with previous ones. The current time is {now}. "
                f"Since data is aggregated, this may or may not represent a new candle. "
                f"Only if there's an entry opportunity, tell me the direction (long or short), take-profit, stop-loss, and contextual R1–R4 and S1–S4 levels based on the previous data. "
                f"If not, just analyze the candle. Give me only the conclusion. "
                f"Please, analyze your strategy carefully, and try to avoid traps. Please indicate when you see a trap. "
                f"Be especially cautious when DensitySpread_Mean is positive, as this may suggest liquidity is more easily accessed at lower price levels. "
                f"In such cases, a rising price might be a trap to attract buyers before sellers re-enter aggressively. "
                f"Likewise, a negative DensitySpread_Mean may indicate buy-side liquidity is more accessible above, so a falling price could be a trap to attract sellers. "
                f"If an entry has already been defined, continue analyzing the strategy and indicate the right time to exit. "
                f"Also, let me know when we might still be holding the position after price touches any contextual level. "
                f"If the strategy is no longer valid, reset everything and look for a new opportunity:      "
                f"{latest_line}"
            )

            response = send_prompt_to_chatgpt(prompt)
            print_output(response)

try:
    run_analysis()
except KeyboardInterrupt:
    cleanup_and_exit()
