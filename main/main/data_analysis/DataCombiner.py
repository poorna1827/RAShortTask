# Load the data from both CSV files.
# Convert the 'Date/Time' column in the first CSV file and the 'local_time' column in the second CSV to datetime objects for accurate comparison.
# For each record in the first CSV file, find the record in the second CSV file with the closest 'local_time' to its 'Date/Time'.
# Merge the relevant columns from the first CSV file into the corresponding rows in the second CSV file, based on the closest match found in step 3.
# Export the merged data into a new CSV file.

import pandas as pd
from datetime import datetime
from pathlib import Path

# Define the file paths
paper_trading_path = Path(r"C:\wt\mini_wt\time_diff\test_order_20240208_1.csv")
tws_real_order_path = Path(r"C:\wt\mini_wt\time_diff\DU7242591_20240208.csv")

# Load the data
mini_wt_df = pd.read_csv(paper_trading_path)
tws_real_df = pd.read_csv(tws_real_order_path)

# Store original string representations
mini_wt_df['local_time_original'] = mini_wt_df['local_time']
tws_real_df['Date/Time_original'] = tws_real_df['Date/Time']

# Convert 'local_time' and 'Date/Time' to datetime objects for comparison
mini_wt_df['local_time'] = pd.to_datetime(mini_wt_df['local_time']).dt.tz_localize(None)
tws_real_df['Date/Time'] = pd.to_datetime(tws_real_df['Date/Time']).dt.tz_localize(None)


# Ensure both columns are tz-naive
# If they were tz-aware, you could convert them to a specific timezone using dt.tz_convert('timezone') or make them tz-naive using dt.tz_localize(None)

# Function to find the index of the row in mini_wt_df with the closest 'local_time'
import pandas as pd


# Assuming mini_wt_df and aapl_tws_real_df are already defined and loaded

def find_closest_time_index(aapl_time):
    # Calculate the time difference between each mini_wt_df entry and the current AAPL time
    time_diff = mini_wt_df['local_time'] - aapl_time

    # Filter for negative time differences and get the largest (closest past time)
    past_times = time_diff[time_diff < pd.Timedelta(0)]
    if not past_times.empty:
        min_negative_diff_index = past_times.idxmax()
    else:
        min_negative_diff_index = pd.NA  # Use NA or a placeholder to indicate no match

    # Filter for positive time differences and get the smallest (closest future time)
    future_times = time_diff[time_diff >= pd.Timedelta(0)]
    if not future_times.empty:
        min_positive_diff_index = future_times.idxmin()
    else:
        min_positive_diff_index = pd.NA  # Use NA or a placeholder to indicate no match

    # Decide which index to return based on which time difference is smaller in magnitude
    if pd.isna(min_negative_diff_index) and pd.isna(min_positive_diff_index):
        return pd.NA  # Return NA or a suitable placeholder if no match found
    elif pd.isna(min_negative_diff_index):
        return min_positive_diff_index
    elif pd.isna(min_positive_diff_index):
        return min_negative_diff_index
    else:
        # If both past and future times exist, choose the closest one
        if abs(time_diff[min_negative_diff_index]) <= time_diff[min_positive_diff_index]:
            return min_negative_diff_index
        else:
            return min_positive_diff_index


# Apply the function to each row in aapl_tws_real_df
tws_real_df['match_index'] = tws_real_df['Date/Time'].apply(find_closest_time_index)

# Merge the two DataFrames based on the calculated index
merged_df = pd.merge(tws_real_df, mini_wt_df, left_on='match_index', right_index=True, how='left')

# Use the original 'local_time' and 'Date/Time' columns in the final DataFrame
merged_df.rename(columns={'local_time_original_y': 'local_time', 'Date/Time_original_x': 'Date/Time'}, inplace=True)

# Drop the 'match_index' as it's no longer needed
merged_df.drop('match_index', axis=1, inplace=True)

# Reorder and select the columns as per the requirement
selected_columns = ['local_time', 'datetime', 'time_diff', 'open', 'high', 'low', 'close', 'volume', 'openinterest', 'ma',
                    'Symbol', 'Date/Time', 'Quantity', 'T. Price', 'C. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L', 'MTM P/L']
merged_df = merged_df[selected_columns]

# Export the merged DataFrame to a CSV file
output_path = Path(r"C:\wt\mini_wt\time_diff\Analysis\merged_GOOG_20240208.csv")
merged_df.to_csv(output_path, index=False)

print(f"Merged file saved to {output_path}")

