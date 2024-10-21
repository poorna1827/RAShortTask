import os
import pandas as pd

# Define the input and output directories
input_dir = r'C:\FinTech\wt_data\data\three_sources_merged_adjusted'
output_file_path = r'C:\FinTech\wt_data\data\statistics\first_dates_open_yf_vs_ibapi_threshold_0.5.csv'

# Prepare a list to hold the results
results = []
source1 = 'adj_open_yf'
source2 = 'adj_open_ibapi'
threshold = 0.5
cutoff_date = '2024-03-01'

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

        # Calculate the absolute relative difference
        df['abs_relative_diff'] = abs(df[source1] - df[source2]) / df[source1] * 100

        # Find the earliest date where all subsequent diffs are <= 0.5%
        earliest_date = "Not exist"

        for i in range(len(df)):
            if (df['abs_relative_diff'][i:] <= threshold).all():
                earliest_date = df['Date'].iloc[i].strftime('%Y-%m-%d')
                break

        # Append the result to the list
        results.append([stock_ticker, earliest_date])

# Convert the results to a DataFrame and save to the output CSV file
results_df = pd.DataFrame(results, columns=['Stock ticker', 'first_date <= 0.5%'])
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
results_df.to_csv(output_file_path, index=False)

print(f'Output saved to {output_file_path}')
