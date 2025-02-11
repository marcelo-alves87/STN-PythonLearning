import pandas as pd
import numpy as np

# Load your CSV file
def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Datetime'])
    df.sort_values('Datetime', inplace=True)
    return df

# Calculate RSI
def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calculate MACD
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    ema_short = df['Close'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['Close'].ewm(span=long_window, adjust=False).mean()

    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()

    return macd, signal_line

# Calculate Pivot Points, Support, and Resistance Levels
def calculate_pivot_points(df):
    last_date = df['Datetime'].dt.date.max()
    last_day_data = df[df['Datetime'].dt.date == last_date]

    high = last_day_data['High'].max()
    low = last_day_data['Low'].min()
    close = last_day_data['Close'].iloc[-1]

    pp = (high + low + close) / 3
    r1 = (2 * pp) - low
    s1 = (2 * pp) - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)

    m1 = (r2 + r1) / 2
    m2 = (r1 + pp) / 2
    m3 = (pp + s1) / 2
    m4 = (s1 + s2) / 2

    return pp, r1, s1, r2, s2, m1, m2, m3, m4

# Simulate potential prices and calculate indicators
def simulate_prices_and_insights(df, price_range=0.02):
    last_row = df.iloc[-1]
    last_close = last_row['Close']

    price_changes = np.linspace(-price_range, price_range, num=20)  # 20 hypothetical price changes
    potential_prices = last_close * (1 + price_changes)

    pp, r1, s1, r2, s2, m1, m2, m3, m4 = calculate_pivot_points(df)

    insights = []

    for price in potential_prices:
        new_row = pd.DataFrame({
            'Datetime': [last_row['Datetime'] + pd.Timedelta(minutes=5)],
            'Close': [price]
        })

        df_extended = pd.concat([df, new_row], ignore_index=True)
        df_extended['RSI'] = calculate_rsi(df_extended)
        df_extended['MACD'], df_extended['Signal_Line'] = calculate_macd(df_extended)

        rsi = df_extended.iloc[-1]['RSI']
        macd = df_extended.iloc[-1]['MACD']
        signal = df_extended.iloc[-1]['Signal_Line']

        signal_type = ""
        if rsi > 70 and macd > signal:
            signal_type = "Potential Buy (RSI > 70 & Bullish MACD Crossover)"
        elif rsi < 30 and macd < signal:
            signal_type = "Potential Sell (RSI < 30 & Bearish MACD Crossover)"
        elif rsi > 70:
            signal_type = "Overbought (Potential Sell)"
        elif rsi < 30:
            signal_type = "Oversold (Potential Buy)"
        elif macd > signal:
            signal_type = "Bullish Crossover"
        elif macd < signal:
            signal_type = "Bearish Crossover"
        elif 30 < rsi < 70 and macd > signal:
            signal_type = "Moderate Uptrend"
        elif 30 < rsi < 70 and macd < signal:
            signal_type = "Moderate Downtrend"
        else:
            signal_type = "Neutral"

        insights.append((price, rsi, macd, signal, signal_type))

    return insights, (pp, r1, s1, r2, s2, m1, m2, m3, m4)

# Filter insights based on pivot point intervals
def filter_by_intervals(insights, pp, r1, s1, r2, s2, m1, m2, m3, m4):
    intervals = {
        "M1 - R2": (m1, r2),
        "R1 - M1": (r1, m1),
        "M2 - R1": (m2, r1),
        "PP - M2": (pp, m2),
        "M3 - PP": (m3, pp),
        "S1 - M3": (s1, m3),
        "M4 - S1": (m4, s1),
        "S2 - M4": (s2, m4)
    }

    filtered_insights = {key: [] for key in intervals.keys()}

    for price, rsi, macd, signal, signal_type in insights:
        for key, (lower, upper) in intervals.items():
            if lower <= price <= upper:
                filtered_insights[key].append((price, rsi, macd, signal, signal_type))

    # Reverse the order of prices within each interval
    for key in filtered_insights:
        filtered_insights[key] = sorted(filtered_insights[key], key=lambda x: -x[0])

    return filtered_insights

# Main function
def main():
    file_path = 'stock_dfs/SBSP3.csv'  # Replace with your file path
    df = load_data(file_path)

    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['Signal_Line'] = calculate_macd(df)

    insights, (pp, r1, s1, r2, s2, m1, m2, m3, m4) = simulate_prices_and_insights(df)
    filtered_insights = filter_by_intervals(insights, pp, r1, s1, r2, s2, m1, m2, m3, m4)

    print("Insights by Intervals:")
    for interval, data in filtered_insights.items():
        if data:
            print(f"\n{interval}:")
            print("Price\tRSI\tMACD\tSignal Line\tInsight")
            for price, rsi, macd, signal, signal_type in data:
                print(f"{price:.2f}\t{rsi:.2f}\t{macd:.2f}\t{signal:.2f}\t{signal_type}")

    print("\nPivot Points:")
    print(f"PP: {pp:.2f}, R1: {r1:.2f}, S1: {s1:.2f}, R2: {r2:.2f}, S2: {s2:.2f}, M1: {m1:.2f}, M2: {m2:.2f}, M3: {m3:.2f}, M4: {m4:.2f}")

if __name__ == "__main__":
    main()
