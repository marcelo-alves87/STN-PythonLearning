import pandas as pd
import numpy as np

# Load the dataset
file_path = 'stock_dfs/SBSP3.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Convert 'Datetime' to datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Sort data by date (if not already sorted)
data = data.sort_values('Datetime')

# Calculate True Range (TR)
data['TR'] = data[['High', 'Low', 'Close']].apply(
    lambda row: max(row['High'] - row['Low'], abs(row['High'] - row['Close']), abs(row['Low'] - row['Close'])),
    axis=1
)

# ATR Method (Wilder's ATR used for simplicity)
n = 14  # Lookback period
data['ATR'] = np.nan
data.loc[n-1, 'ATR'] = data['TR'][:n].mean()  # Initial ATR as simple average of TR
for i in range(n, len(data)):
    data.loc[i, 'ATR'] = (
        (data.loc[i-1, 'ATR'] * (n-1) + data.loc[i, 'TR']) / n
    )

# Calculate Moving Averages (50-day and 200-day MAs)
data['50_MA'] = data['Close'].rolling(window=50).mean()
data['200_MA'] = data['Close'].rolling(window=200).mean()

# Filter the data for the most recent day (last day in the data)
recent_data = data.iloc[-1]

# Get ATR value and closing price from the last available data point
atr = recent_data['ATR']
close_price = recent_data['Close']
high_price = recent_data['High']
low_price = recent_data['Low']

# Calculate the entry, stop loss, target1, and target2 for both bullish and bearish strategies
entry_point = close_price  # Enter at current price
stop_loss_bullish = close_price - atr  # 1x ATR below entry for bullish
target1_bullish = close_price + atr  # 1x ATR above entry for bullish
target2_bullish = close_price + 2 * atr  # 2x ATR above entry for bullish

# Partial targets for Bullish
partial_target1_bullish = entry_point + (target1_bullish - entry_point) * 0.5  # Halfway between entry and target1
partial_target2_bullish = target1_bullish + (target2_bullish - target1_bullish) * 0.5  # Halfway between target1 and target2

# Bullish Strategy
print("\nBullish Strategy:")
print(f"  Entry Point: {entry_point:.2f}")
print(f"  Stop Loss: {stop_loss_bullish:.2f}")
print(f"  Target 1: {target1_bullish:.2f}")
print(f"  Target 2: {target2_bullish:.2f}")
print(f"  Partial Target 1: {partial_target1_bullish:.2f}")
print(f"  Partial Target 2: {partial_target2_bullish:.2f}")

entry_point = close_price  # Enter at current price
stop_loss_bearish = close_price + atr  # 1x ATR above entry for bearish
target1_bearish = close_price - atr  # 1x ATR below entry for bearish
target2_bearish = close_price - 2 * atr  # 2x ATR below entry for bearish

# Partial targets for Bearish
partial_target1_bearish = entry_point - (entry_point - target1_bearish) * 0.5  # Halfway between entry and target1
partial_target2_bearish = target1_bearish - (target1_bearish - target2_bearish) * 0.5  # Halfway between target1 and target2

# Bearish Strategy
print("\nBearish Strategy:")
print(f"  Entry Point: {entry_point:.2f}")
print(f"  Stop Loss: {stop_loss_bearish:.2f}")
print(f"  Target 1: {target1_bearish:.2f}")
print(f"  Target 2: {target2_bearish:.2f}")
print(f"  Partial Target 1: {partial_target1_bearish:.2f}")
print(f"  Partial Target 2: {partial_target2_bearish:.2f}")

# Calculate Pivot, Support and Resistance levels
pivot = (high_price + low_price + close_price) / 3
r1 = 2 * pivot - low_price
r2 = pivot + (high_price - low_price)
s1 = 2 * pivot - high_price
s2 = pivot - (high_price - low_price)

# Mid points between Pivot, Resistance and Support levels
m1 = (pivot + r1) / 2  # Mid between Pivot and Resistance 1
m2 = (pivot + s1) / 2  # Mid between Pivot and Support 1
m3 = (r1 + r2) / 2  # Mid between Resistance 1 and Resistance 2
m4 = (s1 + s2) / 2  # Mid between Support 1 and Support 2

# Print Pivot, Support, Resistance, and Mid points
print("\nPivot, Support, Resistance and Mid Points:")
print(f"  Pivot: {pivot:.2f}")
print(f"  Resistance 1 (R1): {r1:.2f}")
print(f"  Resistance 2 (R2): {r2:.2f}")
print(f"  Support 1 (S1): {s1:.2f}")
print(f"  Support 2 (S2): {s2:.2f}")
print(f"  Mid Point 1 (M1): {m1:.2f}")
print(f"  Mid Point 2 (M2): {m2:.2f}")
print(f"  Mid Point 3 (M3): {m3:.2f}")
print(f"  Mid Point 4 (M4): {m4:.2f}")

# Determine Bullish or Bearish Prediction for the next day based on Moving Averages
if recent_data['50_MA'] > recent_data['200_MA']:
    trend_prediction = "Bullish"
elif recent_data['50_MA'] < recent_data['200_MA']:
    trend_prediction = "Bearish"
else:
    trend_prediction = "Neutral"

print(f"\nPrediction for the next day: {trend_prediction}")
