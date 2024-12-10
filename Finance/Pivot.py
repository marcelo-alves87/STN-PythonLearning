import pandas as pd

# Load the dataset
file_path = 'stock_dfs/SBSP3.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Convert 'Datetime' to datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Sort data by date (if not already sorted)
data = data.sort_values('Datetime')

# Ensure the data has the required columns
required_columns = ['High', 'Low', 'Close', 'Datetime']
if not all(col in data.columns for col in required_columns):
    raise ValueError(f"The dataset must contain the following columns: {', '.join(required_columns)}")

# Create a DataFrame to store pivot points
pivot_points = []

# Iterate through the data starting from the second day
for i in range(1, len(data)):
    # Get the previous day's data
    prev_day = data.iloc[i - 1]

    # Calculate Pivot Points (PP), Resistances (R1, R2), Supports (S1, S2), and middle points
    pp = round((prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3, 2)
    r1 = round(2 * pp - prev_day['Low'], 2)
    s1 = round(2 * pp - prev_day['High'], 2)
    r2 = round(pp + (prev_day['High'] - prev_day['Low']), 2)
    s2 = round(pp - (prev_day['High'] - prev_day['Low']), 2)

    # Middle points
    m1 = round((pp + r1) / 2, 2)
    m2 = round((pp + s1) / 2, 2)
    m3 = round((r1 + r2) / 2, 2)
    m4 = round((s1 + s2) / 2, 2)

    # Distances
    distance_pp_r1 = round(abs(pp - r1), 2)
    distance_pp_s1 = round(abs(pp - s1), 2)

    # Append results to the pivot_points list
    pivot_points.append({
        'Date': data.iloc[i]['Datetime'].date(),
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
    })

# Convert the pivot points list to a DataFrame
pivot_points_df = pd.DataFrame(pivot_points)

# Configure pandas to display all columns
pd.set_option('display.max_columns', None)

# Print the DataFrame
print(pivot_points_df)

# Reset to default settings after printing (optional)
pd.reset_option('display.max_columns')
