import pandas as pd
import numpy as np
import pdb
from tabulate import tabulate

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
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)
    r4 = r3 + (r3 - r2)
    s4 = s3 - (s2 - s3)

    m1 = (r2 + r1) / 2
    m2 = (r1 + pp) / 2
    m3 = (pp + s1) / 2
    m4 = (s1 + s2) / 2
    m5 = (r3 + r2) / 2
    m6 = (r4 + r3) / 2
    m7 = (s3 + s2) / 2
    m8 = (s4 + s3) / 2

    return pp, r1, s1, r2, s2, r3, s3, r4, s4, m1, m2, m3, m4, m5, m6, m7, m8

# Simulate potential prices and calculate indicators
def simulate_prices_and_insights(df, price_range=0.02):
    last_row = df.iloc[-1]
    last_close = last_row['Close']

    price_changes = np.linspace(-price_range, price_range, num=20)
    potential_prices = last_close * (1 + price_changes)

    pp, r1, s1, r2, s2, r3, s3, r4, s4, m1, m2, m3, m4, m5, m6, m7, m8 = calculate_pivot_points(df)

    insights = []
    potential_buys = []
    potential_sells = []
    bullish_crossovers = []
    bearish_crossovers = []

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
            potential_buys.append((price, rsi, macd, signal, "Potential Sell OR Profit-taking for Long-Buying (Overbought, Momentum Up)"))
        elif rsi < 30 and macd < signal:
            potential_sells.append((price, rsi, macd, signal, "Potential Buy OR Profit-taking for Short-Selling (Oversold, Momentum Down)"))
        elif rsi > 70:
            signal_type = "Overbought (Reversal Down)"
        elif rsi < 30:
            signal_type = "Oversold (Potential Reversal Up)"
        elif macd > signal:
            bullish_crossovers.append((price, rsi, macd, signal, "Bullish Crossover"))
        elif macd < signal:
            bearish_crossovers.append((price, rsi, macd, signal, "Bearish Crossover"))
        elif 30 < rsi < 70 and macd > signal:
            signal_type = "Moderate Uptrend"
        elif 30 < rsi < 70 and macd < signal:
            signal_type = "Moderate Downtrend"
        else:
            signal_type = "Neutral"

        if signal_type:
            insights.append((price, rsi, macd, signal, signal_type))

    if potential_buys:
        min_buy = min(potential_buys, key=lambda x: x[0])
        insights.append(min_buy)

    if potential_sells:
        max_sell = max(potential_sells, key=lambda x: x[0])
        insights.append(max_sell)

    if bullish_crossovers:
        min_bullish = min(bullish_crossovers, key=lambda x: x[0])
        insights.append(min_bullish)

    if bearish_crossovers:
        max_bearish = max(bearish_crossovers, key=lambda x: x[0])
        insights.append(max_bearish)

    return insights, (pp, r1, s1, r2, s2, r3, s3, r4, s4, m1, m2, m3, m4, m5, m6, m7, m8)

# Filter insights based on pivot point intervals
def filter_by_intervals(insights, pp, r1, s1, r2, s2, r3, s3, r4, s4, m1, m2, m3, m4, m5, m6, m7, m8):
    intervals = {
        "M6 - R4": (m6, r4),
        "R3 - M6": (r3, m6),
        "M5 - R3": (m5, r3),
        "R2 - M5": (r2, m5),
        "M1 - R2": (m1, r2),
        "R1 - M1": (r1, m1),
        "M2 - R1": (m2, r1),
        "PP - M2": (pp, m2),
        "M3 - PP": (m3, pp),
        "S1 - M3": (s1, m3),
        "M4 - S1": (m4, s1),
        "S2 - M4": (s2, m4),
        "M7 - S2": (m7, s2),
        "S3 - M7": (s3, m7),
        "M8 - S3": (m8, s3),
        "S4 - M8": (s4, m8)
    }

    filtered_insights = {key: [] for key in intervals.keys()}

    for price, rsi, macd, signal, signal_type in insights:
        for key, (lower, upper) in intervals.items():
            if lower <= price <= upper:
                filtered_insights[key].append((price, rsi, macd, signal, signal_type))

    for key in filtered_insights:
        filtered_insights[key] = sorted(filtered_insights[key], key=lambda x: -x[0])

    return filtered_insights

def display_pivot_points_table(pivot_points):
    pivot_labels = ["PP", "R1", "S1", "R2", "S2", "R3", "S3", "R4", "S4",
                    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]
    
    pivot_dict = dict(zip(pivot_labels, pivot_points))  # Convert tuple to dictionary

    sorted_pivot_points = sorted(pivot_dict.items(), key=lambda x: -x[1])  # Sort by value descending

    table = [[key, f"{value:.2f}"] for key, value in sorted_pivot_points]
    print(f"\nPivot Points:")
    print(tabulate(table, headers=["Level", "Value"], tablefmt="grid"))



# Main function
def main(date=None):
    file_path = 'stock_dfs/SBSP3.csv'
    df = load_data(file_path)

    if date:
        df = df[df['Datetime'].dt.date <= pd.to_datetime(date).date()]
        if df.empty:
            print('No data found')
            return

    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['Signal_Line'] = calculate_macd(df)

    # Display Min/Max prices for the last trading day
    last_date = df['Datetime'].dt.date.max()
    last_day_data = df[df['Datetime'].dt.date == last_date]

    min_price = last_day_data['Low'].min()
    max_price = last_day_data['High'].max()
    min_close_price = last_day_data['Close'].min()
    max_close_price = last_day_data['Close'].max()

    # Calculate averages
    avg_price = (min_price + max_price) / 2
    avg_close_price = (min_close_price + max_close_price) / 2

    # Create the table with a separate column for averages
    min_max_table = [
        ["Maximum Price", f"{max_price:.2f}", ""],
        ["Minimum Price", f"{min_price:.2f}", ""],
        ["Average of Max/Min Prices", "", f"{avg_price:.2f}"],
        ["Maximum Close Price", f"{max_close_price:.2f}", ""],
        ["Minimum Close Price", f"{min_close_price:.2f}", ""],
        ["Average of Max/Min Close Prices", "", f"{avg_close_price:.2f}"]
    ]

    # Print the table
    print(f"\nMax/Min Prices for {last_date}:\n")
    print(tabulate(min_max_table, headers=["Type", "Price", "Average"], tablefmt="grid"))

    insights, pivot_points = simulate_prices_and_insights(df)
    filtered_insights = filter_by_intervals(insights, *pivot_points)

    last_date = df['Datetime'].dt.date.max()  # Get the last available date
    next_date = last_date + pd.Timedelta(days=1)  # Get the next day

    print(f"\nInsights by Intervals for {next_date}:")
    for interval, data in filtered_insights.items():
        if data:
            print(f"\n{interval}:")
            table = [[f"{price:.2f}", f"{rsi:.2f}", f"{macd:.2f}", f"{signal:.2f}", signal_type] for price, rsi, macd, signal, signal_type in data]
            print(tabulate(table, headers=["Price", "RSI", "MACD", "Signal Line", "Insight"], tablefmt="grid"))


    display_pivot_points_table(pivot_points)

   

if __name__ == "__main__":
    #Example of usage
    #main('2025-02-20')
    main('2025-02-24')
