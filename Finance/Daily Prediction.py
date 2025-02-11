import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the dataset
data = pd.read_csv('stock_dfs/SBSP3.csv')

# Convert 'Datetime' to datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])
data['Date'] = data['Datetime'].dt.date

# Filter data for the last date
last_data = data[data['Date'] == data.iloc[-1].Datetime.date()]

# Historical data for model training
historical_data = data[data['Date'] < data.iloc[-1].Datetime.date()]

# Calculate Simple Moving Average (SMA) and Relative Strength Index (RSI)
def calculate_sma(series, window=10):
    return series.rolling(window=window).mean()

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Apply indicators
last_data.loc[:, 'SMA_10'] = calculate_sma(last_data['Close'], window=10)
last_data.loc[:, 'RSI'] = calculate_rsi(last_data['Close'], window=14)

historical_data.loc[:, 'SMA_10'] = calculate_sma(historical_data['Close'], window=10)
historical_data.loc[:, 'RSI'] = calculate_rsi(historical_data['Close'], window=14)

# Drop NaN values resulting from indicators
last_data.dropna(subset=['SMA_10', 'RSI'], inplace=True)
historical_data.dropna(subset=['SMA_10', 'RSI'], inplace=True)

# Prepare features and target
def generate_target(group):
    open_price = group['Open'].iloc[0]
    close_price = group['Close'].iloc[-1]
    return int(close_price > open_price)

targets = historical_data.groupby('Date').apply(generate_target).dropna()

# Features: SMA_10, RSI, Volume
features = historical_data.groupby('Date')[['SMA_10', 'RSI', 'Volume']].mean().loc[targets.index]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.2, random_state=42)

# Model Training
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# Model Evaluation
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Prediction for the Next Day using Last Day features
last_data_features = last_data[['SMA_10', 'RSI', 'Volume']].mean().values.reshape(1, -1)

if last_data_features.shape[1] == 3:
    prediction = clf.predict(last_data_features)[0]
    proba = clf.predict_proba(last_data_features)[0]

    # Result
    result = "\ud83d\udcc8 Bullish" if prediction == 1 else "\ud83d\udcc9 Bearish"
    confidence = max(proba) * 100

    print(f"Prediction for daily price movement: {result} with confidence {confidence:.2f}%")
else:
    print("Insufficient data for prediction.")
