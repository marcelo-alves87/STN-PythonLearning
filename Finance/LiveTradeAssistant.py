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
        close = doc["close"]
        high = doc["high"]
        low = doc["low"]
        open_ = doc["open"]
        volume = doc["volume"]
        density = doc.get("DensitySpread_Mean", "")
        rawspread = doc.get("RawSpread_Mean", "")
        liquidity = doc.get("Liquidity_Mean", "")
        pressure = doc.get("Pressure_Mean", "")

        line = (
            f"| {ts} | {close} | {high} | {low} | {open_} | {volume} | "
            f"{density} | {rawspread} | {liquidity} | {pressure} |"
        )
        lines.append(line)
    return " ".join(lines)

def prompt_previous_date(date, first_candle):
    last_day = collection.find({"time": {"$lt": first_candle}}).sort("time", -1).limit(1)[0]["time"].strftime("%Y-%m-%d")
    start_prev_day = pd.to_datetime(last_day)
    end_prev_day = start_prev_day + pd.Timedelta(days=1)
    prev_docs = list(collection.find({
        "time": {
            "$gte": start_prev_day,
            "$lt": end_prev_day
        }
    }).sort("time", 1))
    if prev_docs:
        open_prev_day = prev_docs[0]["open"]
        close_prev_day = prev_docs[-1]["close"]
        high_prev_day = max(doc["high"] for doc in prev_docs)
        low_prev_day = min(doc["low"] for doc in prev_docs)
    else:
        open_prev_day = close_prev_day = high_prev_day = low_prev_day = "N/A"

    prev_day_ohlc_line = (
        f"(Prev Day OHLC - Open: {open_prev_day}, High: {high_prev_day}, "
        f"Low: {low_prev_day}, Close: {close_prev_day})"
    )

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    prompt = (
        f"Now it's {date}. Please analyze the previous trading day's data and give me only the conclusion. "
        f"Keep the response concise but informative, avoiding complex analysis. "
        f"Here is the previous trading day data summary: "
        f"{prev_day_ohlc_line}"
    )


    send_prompt_to_chatgpt(prompt)
    

def run_analysis(date=None):

    # Get dynamic first candle time
    if date:
        today_start = datetime.strptime(date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    prompt_previous_date(date=date, first_candle=today_start)
    
    while True:
        cursor = collection.find({"time": {"$gt": today_start}}).sort("time", 1)
        candle = next(cursor, None)
        if not candle:
            time.sleep(30)
            continue
        else:
            break

    last_processed_minute = None
    submit_prompt = True

    while True:
        now = datetime.now()
        current_minute = now.replace(second=0, microsecond=0)
        now_str = now.strftime('%H:%M')

        if date:
            current_time = candle["time"]
            now_str = current_time.strftime('%H:%M')
            latest = get_today_data(current_timestamp=now_str, date=date)
        else:
            latest = get_today_data()

        latest_lines = format_candle_lines(latest)

        prompt = (
            f"Continue analyzing this 5-minute candle in context with the list below. The current time is {now_str}. "
            f"Since data is aggregated, this may or may not represent a new candle. "
            f"If there's an entry opportunity, tell me in details the direction (long or short), take-profit, stop-loss, and contextual R1–R2 and S1–S2 levels based on previous data. "
            f"If not, just analyze the candle and give me only the conclusion. "
            f"Pay close attention to DensitySpread_Mean: when positive, it may suggest liquidity is more accessible below, making upward moves *potential* bull traps; "
            f"when negative, it may suggest easier liquidity above, making downward moves *potential* bear traps. "
            f"However, rising prices with positive Density or falling prices with negative Density are not necessarily traps — context and confirmation matter. "
            f"Do not identify entry opportunities when RawSpread is greater or equal to 0.09, as the spread makes the cost of entry too high. "
            f"If an entry has already been defined, update the strategy and indicate if it's time to exit or continue holding. "
            f"Let me know if we're still holding a position after hitting any contextual level. "
            f"If the setup is no longer valid, reset and search for a new opportunity. "
            f"Keep the response concise but informative, avoiding complex analysis. "
            f"{latest_lines}"
        )

        if submit_prompt:
            send_prompt_to_chatgpt(prompt)

        if date:
            input('Waiting for the user ...')
            candle = next(cursor, None)
        else:
            # Update last processed minute only after prompt was sent
            if current_minute != last_processed_minute:
                last_processed_minute = current_minute
                submit_prompt = True
            else:
                submit_prompt = False

            time.sleep(1)

            


try:
    run_analysis()
except KeyboardInterrupt:
    cleanup_and_exit()
