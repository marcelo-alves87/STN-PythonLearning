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
output_folder = 'ibov_data'
os.makedirs(output_folder, exist_ok=True)

# Set date range (last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

# Download with retry logic
def download_with_retry(ticker, retries=1, delay=5):
    ticker_clean = ticker.replace('.SA', '')
    output_path = os.path.join(output_folder, f"{ticker_clean}.csv")
    
    # Check if file already exists
    if os.path.exists(output_path):
        try:
            df = pd.read_csv(output_path, parse_dates=['Date'])
            print(f"[{ticker}] loaded from cache")
            return df
        except Exception as e:
            print(f"[{ticker}] Failed to read cached file: {e}")
    
    # If not cached, attempt download
    for attempt in range(retries):
        try:
            df = yf.download(ticker, interval='1d', start=start_str, end=end_str, progress=False, auto_adjust=True)
            print(f"[{ticker}] downloaded successfully")
            return df
        except Exception as e:
            print(f"[{ticker}] Attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    return None


# Step 1: Calculate average volume for sorting
volume_data = []

for ticker in yahoo_tickers:
    df = download_with_retry(ticker)
    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        try:
            avg_volume = float(df['Volume'].mean())
        except Exception:
            avg_volume = 0.0
        volume_data.append((ticker, avg_volume))
        print(f"[{ticker}] downloaded successfully")
    else:
        volume_data.append((ticker, 0.0))
        print(f"[{ticker}] No data or download failed.")

# Step 2: Sort tickers by avg volume (descending)
sorted_tickers = [ticker for ticker, _ in sorted(volume_data, key=lambda x: x[1], reverse=True)]

# Optional: Show top tickers by volume
print("\nTop tickers by average volume:")
for ticker, vol in sorted(volume_data, key=lambda x: x[1], reverse=True):
    print(f"{ticker}: {vol:,.0f}")

# Step 3: Download and save CSVs in sorted order
for ticker_yf in sorted_tickers:
    ticker_clean = ticker_yf.replace('.SA', '')
    print(f"\nDownloading full data for: {ticker_yf}")
    df = download_with_retry(ticker_yf)
    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Date'] = pd.to_datetime(df['Date']) - timedelta(hours=3)
        df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
        output_path = os.path.join(output_folder, f"{ticker_clean}.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
    else:
        print(f"[{ticker_yf}] No data or download failed.")
