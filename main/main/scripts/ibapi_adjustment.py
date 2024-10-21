import os
import pandas as pd

# Define the input and output directories
input_dir = r'C:\FinTech\mini_wt\data\ib_api'
output_dir = r'C:\FinTech\mini_wt\data\ibapi_adjusted'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List all CSV files in the input directory
csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

for csv_file in csv_files:
    # Define the input and output file paths
    input_file_path = os.path.join(input_dir, csv_file)
    output_file_path = os.path.join(output_dir, f'{os.path.splitext(csv_file)[0]}_ibapi_adjusted.csv')

    # Read the CSV file
    df = pd.read_csv(input_file_path)

    # Calculate Adjustment_rate as Adj Close divided by Close
    df['Adjustment_rate'] = df['Adj Close'] / df['Close']

    # Select and re-arrange the required columns
    df_adjusted = df[
        ['date', 'Adj Open', 'Adj High', 'Adj Low', 'Adj Close', 'Volume', 'Adjustment_rate', 'Open', 'High', 'Low',
         'Close']]
    df_adjusted.columns = ['Date', 'Adj Open', 'Adj High', 'Adj Low', 'Adj Close', 'Volume', 'Adjustment_rate', 'Open',
                           'High', 'Low', 'Close']

    # Save the adjusted DataFrame to a new CSV file
    df_adjusted.to_csv(output_file_path, index=False)

    print(f"Adjusted data saved to {output_file_path}")
