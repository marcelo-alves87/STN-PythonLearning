from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import pdb
import signal
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import textwrap

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
collection = client["mongodb"]["prices"]

# Selenium setup using undetected_chromedriver
options = uc.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument("--user-data-dir=C:\ChromeSession")

driver = uc.Chrome(options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
    """
})

driver.get("https://chat.openai.com")

# Graceful exit handler
def cleanup_and_exit(signum=None, frame=None):
    print("\n🔻 Gracefully shutting down...")
    try:
        driver.quit()
        print("✅ Selenium driver closed.")
    except Exception as e:
        print(f"⚠️ Failed to close driver: {e}")
    sys.exit(0)

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

        # Clear and send the prompt
        textarea.clear()
        textarea.send_keys(prompt)

        # Wait until full text appears in the textarea
        WebDriverWait(driver, 10).until(
            lambda d: driver.execute_script("""
                return Array.from(arguments[0].querySelectorAll('p'))
                            .map(p => p.textContent)
                            .join('\\n');
            """, textarea) == prompt
        )

        
        # Then safely press Enter
        textarea.send_keys(Keys.ENTER)

        return wait_for_stable_response()
    except Exception as e:
        return f"⚠️ Error: {e}"


def get_today_data(current_timestamp=None, date=None):
    if date:
        # Start of the day
        start = datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        
        end = datetime.strptime(f"{date} {current_timestamp}", "%Y-%m-%d %H:%M")       

        query = {"time": {"$gt": start, "$lte": end}}
    else:
        # Default: from today 00:00 until now
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=0, microsecond=0)
        query = {"time": {"$gt": start, "$lte": now}}

    return list(collection.find(query).sort("time", 1))


def format_candle_lines(docs):
    lines = [
        "| time | close | high | low | open | volume | Density | RawSpread | Liquidity | Pressure |"
    ]
    for doc in docs:
        ts = pd.to_datetime(doc["time"]).strftime("%Y-%m-%d %H:%M:%S")
        close = round(doc["close"], 2)
        high = round(doc["high"], 2)
        low = round(doc["low"], 2)
        open_ = round(doc["open"], 2)
        volume = round(doc["volume"], 2)
        density = round(doc.get("DensitySpread_Mean", 0), 2) if "DensitySpread_Mean" in doc else ""
        rawspread = round(doc.get("RawSpread_Mean", 0), 2) if "RawSpread_Mean" in doc else ""
        liquidity = round(doc.get("Liquidity_Mean", 0), 2) if "Liquidity_Mean" in doc else ""
        pressure = round(doc.get("Pressure_Mean", 0), 2) if "Pressure_Mean" in doc else ""

        line = (
            f"| {ts} | {close} | {high} | {low} | {open_} | {volume} | "
            f"{density} | {rawspread} | {liquidity} | {pressure} |"
        )
        lines.append(line)
    return " ".join(lines)

def prompt_previous_date(date, first_candle):
    # Get the 5 most recent unique trading days before first_candle
    
    last_docs = list(collection.find({"time": {"$lt": first_candle}}).sort("time", -1))

    unique_days = []
    seen = set()

    for doc in last_docs:
        day_str = doc["time"].strftime("%Y-%m-%d")
        if day_str not in seen:
            seen.add(day_str)
            unique_days.append(day_str)
        if len(unique_days) == 5:
            break

    

    # Generate OHLC summary for each of the last 5 days
    summaries = []
    for day_str in reversed(unique_days):  # reverse to go from oldest to newest
        start_day = pd.to_datetime(day_str)
        end_day = start_day + pd.Timedelta(days=1)

        day_docs = list(collection.find({
            "time": {
                "$gte": start_day,
                "$lt": end_day
            }
        }).sort("time", 1))

        if day_docs:
            open_price = day_docs[0]["open"]
            close_price = day_docs[-1]["close"]
            high_price = max(doc["high"] for doc in day_docs)
            low_price = min(doc["low"] for doc in day_docs)

            summary = (
                f"[{day_str} OHLC - Open: {open_price}, High: {high_price}, "
                f"Low: {low_price}, Close: {close_price}]"
            )
        else:
            summary = f"[{day_str} OHLC - No data available]"

        summaries.append(summary)

    prev_day_ohlc_lines = " ".join(summaries)

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    prompt = (
        f"Now it's {date}. Analyze the previous 5 trading days' data and provide a concise conclusion about market context and evolving bias. "
        f"Identify any significant levels or patterns that may influence today's trading decisions, but do not speculate about future entries yet. "
        f"Keep the response short, clear, and focused — avoid complex analysis. "
        f"Here is the summary of the last 5 trading days:    "
        f"{prev_day_ohlc_lines}"
    )
    
    send_prompt_to_chatgpt(prompt)

def get_latest_mongo_doc():
    return client["mongodb"]["scraped_prices"].find_one(sort=[("time", -1)])

def round_down_to_nearest_5(dt):
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)

    
def run_analysis(date=None):

    # Get dynamic first candle time
    if date:
        today_start = datetime.strptime(date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    prompt_previous_date(date=date, first_candle=today_start)

    if date:
        input('Waiting for the user ...')

    while True:
        docs = list(collection.find({"time": {"$gt": today_start}}).sort("time", 1))
        if not docs:
            time.sleep(30)
            continue
        else:
            break

    count = 0
    first_data = (len(docs) == 1) if not date else True
    candle = docs[count]
    last_processed_minute = None

    while True:
        
        if date:
            current_time = candle["time"]
            now_str = current_time.strftime('%H:%M')
            today = current_time.strftime('%Y-%m-%d')
            latest = get_today_data(current_timestamp=now_str, date=date)
        else:
            latest_doc = get_latest_mongo_doc()
            mongo_time = latest_doc['time']            
            candle_time = round_down_to_nearest_5(mongo_time)
            if last_processed_minute is None or candle_time > last_processed_minute:
                current_time = mongo_time
                now_str = current_time.strftime('%H:%M')
                today = current_time.strftime('%Y-%m-%d')
                latest = get_today_data()
                last_processed_minute = candle_time
            else:
                time.sleep(1)
                continue

        latest_lines = format_candle_lines(latest)

        if first_data:

            prompt = (
                f"This is the first 5-minute candle of today ({today}) at {now_str}. "
                f"Please analyze this candle in the context of market open behavior. "
                f"Identify any early signs of bullish or bearish sentiment based on this single candle.         "
                f"{latest_lines}"
            )
            first_data = False
        else:

            prompt = (
                f"Analyze the most recently *closed* 5-minute candle in the context of the list below. The current time is {now_str}. "
                f"If a newer candle exists, it's very import consider its OHLCV values in your analysis — do not analyze it as a completed candle. "
                f"Base your conclusions primarily on the last fully closed candle and the recent OHLC opened candle, if it exists. "
                f"If there's an entry opportunity, explain clearly the direction (long or short), take-profit, stop-loss, and contextual R1–R2 and S1–S2 levels based on previous data. "
                f"If not, just analyze the closed candle and provide only the conclusion. "
                f"Pay close attention to DensitySpread_Mean: when positive, it may suggest liquidity is more accessible below, making upward moves *potential* bull traps; "
                f"when negative, it may suggest easier liquidity above, making downward moves *potential* bear traps. "
                f"However, rising prices with positive Density or falling prices with negative Density are not necessarily traps — context and confirmation matter. "
                f"Do not identify entry opportunities when RawSpread is greater or equal to 0.09, as the spread makes the cost of entry too high. "
                f"If an entry has already been defined, update the strategy and indicate if it's time to exit or continue holding. "
                f"Let me know if we're still holding a position after hitting any contextual level. "
                f"If the setup is no longer valid, reset and search for a new opportunity. "
                f"Keep the response concise but informative, avoiding overly complex reasoning. "
                f"{latest_lines}"
            )



        send_prompt_to_chatgpt(prompt)

        if date:
            input('Waiting for the user ...')
            count += 1
            if count < len(docs):
                candle = docs[count]
            else:
                break

            


try:
    run_analysis()
except KeyboardInterrupt:
    cleanup_and_exit()
