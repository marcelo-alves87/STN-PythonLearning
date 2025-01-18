import pandas as pd

def calculate_pivot_points(date, high, low, close):
    pp = round((high + low + close) / 3, 2)
    r1 = round(2 * pp - low, 2)
    s1 = round(2 * pp - high, 2)
    r2 = round(pp + (high - low), 2)
    s2 = round(pp - (high - low), 2)
    m1 = round((pp + r1) / 2, 2)
    m2 = round((pp + s1) / 2, 2)
    m3 = round((r1 + r2) / 2, 2)
    m4 = round((s1 + s2) / 2, 2)
    distance_pp_r1 = round(abs(pp - r1), 2)
    distance_pp_s1 = round(abs(pp - s1), 2)
    return {
        'Date': date,
        'PP': pp,
        'R1': r1,
        'S1': s1,
        'R2': r2,
        'S2': s2,
        'M1': m1,
        'M2': m2,
        'M3': m3,
        'M4': m4,
        'Distance_PP_R1': distance_pp_r1,
        'Distance_PP_S1': distance_pp_s1
    }

# Load the dataset
file_path = 'stock_dfs/SBSP3.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Convert 'Datetime' to datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Set 'Datetime' as the index for resampling
data.set_index('Datetime', inplace=True)

# Resample the data to daily timeframe (or other timeframes as needed)
# Aggregate the high, low, and close prices
daily_data = data.resample('1D').agg({
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
}).dropna()  # Drop rows with incomplete data

# Create a DataFrame to store pivot points
pivot_points = []

# Iterate through the data starting from the second day
for i in range(1, len(daily_data)):
    prev_day = daily_data.iloc[i - 1]
    current_date = daily_data.index[i].date()
    pivot_data = calculate_pivot_points(current_date, prev_day['High'], prev_day['Low'], prev_day['Close'])
    pivot_points.append(pivot_data)

# Calculate pivot points for the day after the last index
last_day = daily_data.iloc[-1]
next_day_pivot = calculate_pivot_points(
    (daily_data.index[-1] + pd.Timedelta(days=1)).date(),
    last_day['High'], last_day['Low'], last_day['Close']
)
pivot_points.append(next_day_pivot)

# Convert the pivot points list to a DataFrame
pivot_points_df = pd.DataFrame(pivot_points)

# Configure pandas to display all columns
pd.set_option('display.max_columns', None)

# Print the DataFrame
print(pivot_points_df)

# Reset to default settings after printing (optional)
pd.reset_option('display.max_columns')
