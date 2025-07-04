import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import os
import pdb

# Load and clean tickers
df = pd.read_csv('Free-Float_5-2025.csv', header=None, names=['raw'])
tickers = df['raw'].str.split(';').str[0].str.strip()
tickers = tickers[tickers != 'Codigo']
yahoo_tickers = [ticker + '.SA' for ticker in tickers]

# Create output folder
output_folder = 'ibov_5min_data'
os.makedirs(output_folder, exist_ok=True)

# Set date range (this week)
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
start_str = start_of_week.strftime('%Y-%m-%d')
end_str = today.strftime('%Y-%m-%d')

# Download with retry logic
def download_with_retry(ticker, retries=3, delay=5):
    for attempt in range(retries):
        try:
            df = yf.download(ticker, interval='5m', start=start_str, end=end_str, progress=False)
            return df
        except Exception as e:
            print(f"[{ticker}] Attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    return None

# Loop through tickers
for ticker_yf in yahoo_tickers:
    ticker_clean = ticker_yf.replace('.SA', '')
    print(f"Downloading: {ticker_yf}")
    df = download_with_retry(ticker_yf)
    if df is not None and not df.empty:
        # Flatten columns if MultiIndex is present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Datetime'] = df['Datetime'] - timedelta(hours=3)
        df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
        output_path = os.path.join(output_folder, f"{ticker_clean}.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
    else:
        print(f"[{ticker_yf}] No data or download failed.")
    #time.sleep(2)  # Respect rate limit
