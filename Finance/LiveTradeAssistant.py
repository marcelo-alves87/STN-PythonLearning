import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import pdb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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

# Tkinter setup
root = tk.Tk()
root.title("Live Trade Assistant")
root.geometry("700x500")

text_frame = tk.Frame(root, bg="#f9f9f9")
text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

text_widget = tk.Text(
    text_frame,
    wrap=tk.WORD,
    font=("Segoe UI", 12),
    bg="white",
    fg="#222222",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    spacing1=5,
    spacing2=5,
    spacing3=5
)
text_widget.pack(expand=True, fill=tk.BOTH)
text_widget.insert(tk.END, "Initializing...")
text_widget.pack(expand=True, fill=tk.BOTH)

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
    return f"{ts},{close},{high},{low},{open_},{volume},{density},{rawspread},{liquidity},{pressure}"

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
            prev_lines = [format_candle_line(doc) for doc in prev_docs]
            prev_data = "".join(prev_lines)
            curr_line = format_candle_line(first_doc)

            prompt = (
                f"Please analyze the first 5-minute candle from {TODAY} using the previous trading day's data and give me only the conclusion."
                f"Here is the previous trading day data:"
                f"time,close,high,low,open,volume,DensitySpread_Mean,RawSpread_Mean,Liquidity_Mean,Pressure_Mean"
                f"{prev_data}"
                f"Here is the first candle of the day:"
                f"{curr_line}"
            )
            
            response = send_prompt_to_chatgpt(prompt)
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, response)
            last_checked_time = str(first_doc["time"])
        else:
            time.sleep(60)
            latest = get_latest_data()
            latest_line = format_candle_line(latest)
            prompt = (
                f"Continue analyzing this 5-minute candle. Only if there's an entry opportunity, tell me the direction, take-profit, stop-loss, "
                f"and contextual R1–R4 and S1–S4 levels based on the previous data. If not, just analyze the candle. Remember: give me only the conclusion."
                f" If an entry has already been defined, continue analyzing the strategy and indicate the right time to exit. If the strategy is no longer valid, reset everything and look for a new opportunity:"
                f"{latest_line}"
            )
            response = send_prompt_to_chatgpt(prompt)
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, response)

def start_thread():
    thread = threading.Thread(target=run_analysis, daemon=True)
    thread.start()

start_thread()
root.mainloop()
driver.quit()
