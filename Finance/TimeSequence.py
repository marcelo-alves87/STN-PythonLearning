from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate

# Define market hours
market_open = "10:00"
market_close = "17:50"

# Define Fibonacci reference points
fib_0 = "10:40"  # Level 0
fib_1 = "15:15"  # Level 1 (275 minutes after 10:40)
date_input = "2025-02-17"  # Example date

# Fibonacci ratios to calculate
fib_ratios = [0, 0.382, 0.618, 1, 1.618, 2.618]

# Convert times to datetime objects
fib_0_dt = datetime.strptime(f"{date_input} {fib_0}", "%Y-%m-%d %H:%M")
fib_1_dt = datetime.strptime(f"{date_input} {fib_1}", "%Y-%m-%d %H:%M")
market_open_dt = datetime.strptime(f"{date_input} {market_open}", "%Y-%m-%d %H:%M")
market_close_dt = datetime.strptime(f"{date_input} {market_close}", "%Y-%m-%d %H:%M")

# Compute total minutes from Level 0 to Level 1
total_minutes = int((fib_1_dt - fib_0_dt).total_seconds() // 60)

# Function to calculate Fibonacci time zones while respecting market hours
def calculate_fibonacci_times(base_time, total_minutes, ratios, open_time, close_time):
    fib_times = []
    current_day = base_time.date()

    for ratio in ratios:
        added_minutes = int(total_minutes * ratio)
        new_time = base_time + timedelta(minutes=added_minutes)

        # If new time is beyond market hours, move to the next session
        if new_time.time() > close_time.time():
            new_time = datetime.combine(new_time.date() + timedelta(days=1), open_time.time()) + (new_time - close_time)
            current_day = new_time.date()

        # Format Date and Time properly
        date_str = new_time.strftime("%m-%d")
        time_str = new_time.strftime("%H:%M")

        fib_times.append((date_str, ratio, time_str))

    return fib_times

# Calculate Fibonacci time zones
fib_results = calculate_fibonacci_times(fib_0_dt, total_minutes, fib_ratios, market_open_dt, market_close_dt)

# Create a DataFrame for display
df = pd.DataFrame(fib_results, columns=["Date", "Fibonacci Level", "Value"])

# Print table properly formatted
print(tabulate(df, headers="keys", tablefmt="grid"))
