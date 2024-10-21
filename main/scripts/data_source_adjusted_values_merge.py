import os
import pandas as pd

# Define the paths to the folders
fdb_folder = 'C:/FinTech/mini_wt/data/finance_database_adjusted'
yf_folder = 'C:/FinTech/mini_wt/data/yahoo_adjusted'
ibapi_folder = 'C:/FinTech/mini_wt/data/ibapi_adjusted'
output_folder = 'C:/FinTech/mini_wt/data/three_sources_merged_adjusted'

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Get the list of stock files in fdb and yf folders
fdb_files = os.listdir(fdb_folder)
yf_files = os.listdir(yf_folder)
ibapi_files = os.listdir(ibapi_folder)

# Function to get the base name of the file (without the folder and extension)
def get_base_name(file):
    return os.path.splitext(file)[0]

# Loop through fdb and yf files and merge them with the corresponding ibapi file if it exists
for fdb_file in fdb_files:
    ticker = get_base_name(fdb_file).split('_')[0]  # Extract the stock ticker
    print(f"Processing {ticker}")

    yf_file = fdb_file.replace('_fdb_', '_yf_')
    ibapi_file = fdb_file.replace('_fdb_', '_ibapi_')

    if yf_file in yf_files:
        # Load fdb and yf data
        fdb_df = pd.read_csv(os.path.join(fdb_folder, fdb_file))
        yf_df = pd.read_csv(os.path.join(yf_folder, yf_file))

        # Rename columns for clarity
        fdb_df.rename(columns={'Adj Open': 'adj_open_fdb', 'Adj High': 'adj_high_fdb', 'Adj Low': 'adj_low_fdb',
                               'Adj Close': 'adj_close_fdb', 'Volume': 'volume_fdb'}, inplace=True)
        yf_df.rename(columns={'Adj Open': 'adj_open_yf', 'Adj High': 'adj_high_yf', 'Adj Low': 'adj_low_yf',
                              'Adj Close': 'adj_close_yf', 'Volume': 'volume_yf'}, inplace=True)

        try:
            # Keep only the relevant columns
            fdb_df = fdb_df[['Date', 'adj_open_fdb', 'adj_high_fdb', 'adj_low_fdb', 'adj_close_fdb', 'volume_fdb']]
            yf_df = yf_df[['Date', 'adj_open_yf', 'adj_high_yf', 'adj_low_yf', 'adj_close_yf', 'volume_yf']]

            # Convert Date columns to datetime
            fdb_df['Date'] = pd.to_datetime(fdb_df['Date'])
            yf_df['Date'] = pd.to_datetime(yf_df['Date'])

            # Determine the latest starting date
            latest_start_date = max(fdb_df['Date'].min(), yf_df['Date'].min())

            # Filter dataframes to include only data from the latest starting date
            fdb_df = fdb_df[fdb_df['Date'] >= latest_start_date]
            yf_df = yf_df[yf_df['Date'] >= latest_start_date]

            # Merge fdb and yf dataframes on Date
            merged_df = pd.merge(fdb_df, yf_df, on='Date', how='inner')

            # Check if the corresponding ibapi file exists
            if ibapi_file in ibapi_files:
                ibapi_df = pd.read_csv(os.path.join(ibapi_folder, ibapi_file))
                ibapi_df.rename(columns={'Adj Open': 'adj_open_ibapi', 'Adj High': 'adj_high_ibapi', 'Adj Low': 'adj_low_ibapi',
                                         'Adj Close': 'adj_close_ibapi', 'Volume': 'volume_ibapi'}, inplace=True)
                ibapi_df = ibapi_df[['Date', 'adj_open_ibapi', 'adj_high_ibapi', 'adj_low_ibapi', 'adj_close_ibapi', 'volume_ibapi']]
                ibapi_df['Date'] = pd.to_datetime(ibapi_df['Date'])
                ibapi_df = ibapi_df[ibapi_df['Date'] >= latest_start_date]
                merged_df = pd.merge(merged_df, ibapi_df, on='Date', how='left')
            else:
                merged_df['adj_open_ibapi'] = pd.NA
                merged_df['adj_high_ibapi'] = pd.NA
                merged_df['adj_low_ibapi'] = pd.NA
                merged_df['adj_close_ibapi'] = pd.NA
                merged_df['volume_ibapi'] = pd.NA

            # Reorder the columns
            ordered_columns = [
                'Date',
                'adj_open_fdb', 'adj_open_yf', 'adj_open_ibapi',
                'adj_high_fdb', 'adj_high_yf', 'adj_high_ibapi',
                'adj_low_fdb', 'adj_low_yf', 'adj_low_ibapi',
                'adj_close_fdb', 'adj_close_yf', 'adj_close_ibapi',
                'volume_fdb', 'volume_yf', 'volume_ibapi'
            ]
            merged_df = merged_df[ordered_columns]

            # Save the merged dataframe to a new CSV file
            output_file_path = os.path.join(output_folder, fdb_file.replace('_fdb_', '_merged_'))
            merged_df.to_csv(output_file_path, index=False)

        except KeyError as e:
            print(f"KeyError for {ticker}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {ticker}: {e}")