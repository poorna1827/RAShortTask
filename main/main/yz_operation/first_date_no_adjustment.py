import os
import pandas as pd

def check_next_days(data, index):
    # Check if the next 5 days also have an adjustment rate of 1
    try:
        next_days = data['Adjustment_rate'].iloc[index+1:index+6]
        return 'Yes' if all(next_days == 1) else 'No'
    except:
        return 'No'  # If there are not enough days left in the data

# Define the directory containing adjusted CSV files
input_dir = 'C:\\FinTech\\mini_wt\\data\\ibapi_adjusted'
output_file = 'C:\\FinTech\\mini_wt\\data\\ibapi_adjusted\\first_date_analysis.csv'

results = []

# Process each CSV file in the directory
for filename in os.listdir(input_dir):
    if filename.endswith('_adjusted.csv'):
        file_path = os.path.join(input_dir, filename)
        data = pd.read_csv(file_path)

        # Find the first date where the adjustment rate is 1
        match = data[data['Adjustment_rate'] == 1].iloc[0] if any(data['Adjustment_rate'] == 1) else None
        if match is not None:
            first_date = match['Date']
            index = data.index[data['Date'] == first_date].tolist()[0]
            next_5_days = check_next_days(data, index)
            stock_name = filename.split('_')[0]
            results.append([first_date, next_5_days, stock_name])

# Save results to a CSV file
results_df = pd.DataFrame(results, columns=['First Date', 'Next 5 Days', 'Stock Name'])
results_df.to_csv(output_file, index=False)

print("Analysis complete and results saved.")
