import os
import pandas as pd

# Define the path to the output folder
output_folder = 'C:/FinTech/mini_wt/data/three_sources_merged_adjusted'
result_file = 'C:/FinTech/mini_wt/data/three_sources_merged_adjusted/statistics/three_sources_merged_adjusted_dates.csv'

# Get the list of merged stock files
merged_files = os.listdir(output_folder)

# Prepare a list to store results
results = []

# Loop through each merged stock file and check for the date
for merged_file in merged_files:
    ticker = os.path.splitext(merged_file)[0].split('_')[0]  # Extract the stock ticker
    print(f"Processing {ticker}")

    # Load the merged data
    merged_df = pd.read_csv(os.path.join(output_folder, merged_file))

    # Find the date when adj_open_fdb and adj_open_yf become the same and stay the same
    same_value_start_date = 'No'
    for i in range(len(merged_df)):
        if (merged_df['adj_open_fdb'].iloc[i:] == merged_df['adj_open_yf'].iloc[i:]).all():
            same_value_start_date = merged_df['Date'].iloc[i]
            break

    # Append the result
    results.append([ticker, same_value_start_date])

# Create a DataFrame from the results
results_df = pd.DataFrame(results, columns=['Stock', 'Same_Value_Date'])

# Save the results to a CSV file
results_df.to_csv(result_file, index=False)

print(f"Results saved to {result_file}")
