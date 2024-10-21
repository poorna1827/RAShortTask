import pandas as pd

import os
import pandas as pd

# Define the directories
input_dir = r'C:\\FinTech\\mini_wt\\data\\yahoo_finance'
output_dir = r'C:\\FinTech\\mini_wt\\data\\yahoo_adjusted'

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each CSV file in the directory
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        # Load the data
        file_path = os.path.join(input_dir, filename)
        data = pd.read_csv(file_path)

        # Calculate the adjustment rate and adjusted prices
        data['Adjustment_rate'] = data['Adj Close'] / data['Close']
        data['Adj Open'] = data['Open'] * data['Adjustment_rate']
        data['Adj High'] = data['High'] * data['Adjustment_rate']
        data['Adj Low'] = data['Low'] * data['Adjustment_rate']

        # Prepare the output data
        columns = ['Date', 'Adj Open', 'Adj High', 'Adj Low', 'Adj Close', 'Volume', 'Adjustment_rate', 'Open', 'High', 'Low', 'Close']
        adjusted_data = data[columns]

        # Save the adjusted data
        output_filename = filename.replace('.csv', '_adjusted.csv')
        output_path = os.path.join(output_dir, output_filename)
        adjusted_data.to_csv(output_path, index=False)

print("All files have been processed and adjusted data saved.")
