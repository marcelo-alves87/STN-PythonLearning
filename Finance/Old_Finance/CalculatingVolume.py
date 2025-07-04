import pandas as pd
import os
from datetime import datetime

# === PARAMETERS ===
csv_dir = 'ibov_5min_data'  # Folder with CSVs (e.g., AALR3.csv)
end_hour = '12:00'          # Cutoff time for partial volume (inclusive)

# === FORMATTER FOR K / M / B ===
def format_volume(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    else:
        return str(int(n))

# === CALCULATE VOLUMES FOR A TICKER ===
def calculate_volume_until(file_path, end_hour):
    df = pd.read_csv(file_path, parse_dates=['Datetime'])
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Get earliest time in file
    start_time = df['Datetime'].dt.time.min()
    end_time = pd.to_datetime(end_hour).time()

    # Partial volume (start to end_hour)
    partial_df = df[df['Datetime'].dt.time.between(start_time, end_time)]
    partial_volume = partial_df['Volume'].sum()

    # Total volume (entire day)
    total_volume = df['Volume'].sum()

    ticker = os.path.basename(file_path).replace('.csv', '')
    return ticker, partial_volume, total_volume

# === LOOP THROUGH ALL FILES ===
volume_data = []

for filename in os.listdir(csv_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_dir, filename)
        try:
            ticker, partial_vol, total_vol = calculate_volume_until(file_path, end_hour)
            if partial_vol > 0:
                volume_data.append((ticker, partial_vol, total_vol))
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# === CREATE DATAFRAME WITH RAW VALUES ===
volume_df = pd.DataFrame(volume_data, columns=[
    'Ticker', 'PartialRaw', 'TotalRaw'
])

# Sort by partial raw volume
volume_df.sort_values(by='PartialRaw', ascending=False, inplace=True)

# === ADD FORMATTED DISPLAY COLUMNS ===
volume_df[f'VolumeUntil_{end_hour}'] = volume_df['PartialRaw'].apply(format_volume)
volume_df['TotalDayVolume'] = volume_df['TotalRaw'].apply(format_volume)

# Optional: percentage of volume before end_hour
volume_df['%UntilEndHour'] = (volume_df['PartialRaw'] / volume_df['TotalRaw'] * 100).round(1).astype(str) + '%'

# === FINAL DISPLAY TABLE ===
volume_df = volume_df[['Ticker', f'VolumeUntil_{end_hour}', 'TotalDayVolume', '%UntilEndHour']]

# Print to terminal
print(volume_df.to_string())

# Save to CSV
#output_file = f'volume_summary_until_{end_hour.replace(":", "")}.csv'
#volume_df.to_csv(output_file, index=False)
#print(f"\nSaved summary to: {output_file}")
