import os
import pandas as pd

# Define the input and output directories
input_dir = r'C:\FinTech\wt_data\data\three_sources_merged_adjusted'
output_file_path = r'C:\FinTech\wt_data\data\statistics\volume\volume_first_dates_threshold_5.csv'

# Prepare a list to hold the results
results = []
threshold = 5 # 0.1% threshold
source1 = 'volume_fdb'
source2 = 'volume_yf'
source3 = 'volume_ibapi'

cutoff_date = '2024-03-01'


def calculate_earliest_date(df, source1, source2, threshold):
    df['abs_relative_diff'] = abs(df[source1] - df[source2]) / df[source1] * 100
    df['abs_relative_diff'] = df['abs_relative_diff'].fillna(float('inf'))  # Fill NaN with infinity

    # Find the earliest date where all subsequent diffs are <= threshold
    earliest_date = "Not exist"
    for i in range(len(df)):
        if (df['abs_relative_diff'][i:] <= threshold).all():
            earliest_date = df['Date'].iloc[i].strftime('%Y-%m-%d')
            break
    return earliest_date



# Process each CSV file in the input directory
for filename in os.listdir(input_dir):
    print(f"Processing file {filename}")
    if filename.endswith('.csv'):
        stock_ticker = filename.split('_')[0]
        file_path = os.path.join(input_dir, filename)

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Filter out dates after the cutoff date
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'] <= cutoff_date]

        # Calculate earliest dates for each pair comparison
        earliest_date_fdb_vs_yf = calculate_earliest_date(df, source1, source2, threshold)
        earliest_date_fdb_vs_ibapi = calculate_earliest_date(df, source1, source3, threshold)
        earliest_date_yf_vs_ibapi = calculate_earliest_date(df, source2, source3, threshold)

        # Append the result to the list
        results.append([stock_ticker, earliest_date_fdb_vs_yf, earliest_date_fdb_vs_ibapi, earliest_date_yf_vs_ibapi])

# Convert the results to a DataFrame and save to the output CSV file
results_df = pd.DataFrame(results, columns=['Stock Ticker', 'FDB vs YF', 'FDB vs IBAPI', 'YF vs IBAPI'])
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
results_df.to_csv(output_file_path, index=False)

# Count the number of "Not exist" entries
not_exist_count = (results_df == "Not exist").sum().sum()
print(f'Number of "Not exist" entries: {not_exist_count}')

print(f'Output saved to {output_file_path}')
