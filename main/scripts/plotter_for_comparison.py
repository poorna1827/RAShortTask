import pandas as pd
import matplotlib.pyplot as plt

import pandas as pd
import matplotlib.pyplot as plt

def load_and_adjust_data(filepath, original_date_column, date_format, volume_factor=1):
    # Load data
    data = pd.read_csv(filepath)
    # Normalize column names and ensure 'Date' is the name used for the date column
    data.columns = [col.strip().title() for col in data.columns]
    data.rename(columns={original_date_column.title(): 'Date'}, inplace=True)
    # Convert date to datetime
    data['Date'] = pd.to_datetime(data['Date'], format=date_format)
    # Adjust volume if necessary
    data['Volume'] = data['Volume'] * volume_factor
    return data





def plot_volume_data(fdb_data, yf_data, ibapi_data):
    plt.figure(figsize=(14, 7))

    # Plotting with specific colors and solid lines
    plt.plot(fdb_data['Date'], fdb_data['Volume'], label='Finance Database', color='blue', linewidth=2, linestyle='-')
    plt.plot(yf_data['Date'], yf_data['Volume'], label='Yahoo Finance', color='red', linewidth=2, linestyle='-')
    plt.plot(ibapi_data['Date'], ibapi_data['Volume'], label='Interactive Brokers', color='black', linewidth=2,
             linestyle='-')

    # Title and labels with enhanced font settings
    plt.title('Comparison of Google Volumes from Different Sources', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Volume', fontsize=14)

    # Enhancing the legend
    plt.legend(fontsize=12, loc='upper left')

    # Grid to improve readability
    plt.grid(True)

    # Background color
    plt.gca().set_facecolor('whitesmoke')  # Light gray background color for less strain

    # Show the plot
    plt.show()


def load_and_prepare_data(filepath, date_column, volume_column):
    # Load data
    data = pd.read_csv(filepath)
    # Print column names to check
    print("Columns in the data:", data.columns)
    # Ensure date column is recognized
    if date_column not in data.columns:
        # Attempt to correct common column name issues
        corrected_date_column = next((col for col in data.columns if date_column.lower() in col.lower()), None)
        if corrected_date_column:
            print(f"Correcting date column name from '{corrected_date_column}' to '{date_column}'")
            data.rename(columns={corrected_date_column: date_column}, inplace=True)
        else:
            raise ValueError(f"Date column '{date_column}' not found in data.")
    # Convert date to datetime
    data[date_column] = pd.to_datetime(data[date_column])
    # Normalize volume column names similarly if needed
    data.set_index(date_column, inplace=True)
    return data[[volume_column]]


def plot_relative_volumes(fdb_data, yf_data, ibapi_data):
    # Align data
    combined = pd.concat([fdb_data, yf_data, ibapi_data], axis=1)
    combined.columns = ['FDB', 'YF', 'IBAPI']

    # Calculate relative volumes
    combined['FDB_Relative'] = combined['FDB'] / combined['YF']
    combined['IBAPI_Relative'] = combined['IBAPI'] / combined['YF']

    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(combined.index, combined['FDB_Relative'], label='FDB Relative to YF', color='blue', linewidth=2)
    plt.plot(combined.index, combined['IBAPI_Relative'], label='IBAPI Relative to YF', color='red', linewidth=2)
    plt.title('Relative Volume of FDB and IBAPI to Yahoo Finance', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Relative Volume', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    # Paths to the CSV files
    fdb_path = 'C:/FinTech/mini_wt/yz_data/GOOGL_from_fdb.csv'
    yf_path = 'C:/FinTech/mini_wt/yz_data/GOOGL_daily_data_from_yf.csv'
    ibapi_path = 'C:/FinTech/mini_wt/yz_data/GOOGL_daily_data_from_ibapi.csv'

    # Load and adjust data
    #fdb_data = load_and_adjust_data(fdb_path, 'date', '%m/%d/%Y')
    #yf_data = load_and_adjust_data(yf_path, 'Date', '%Y-%m-%d')
    #ibapi_data = load_and_adjust_data(ibapi_path, 'date', '%Y%m%d', volume_factor=100)

    # Plot the data
    # plot_volume_data(fdb_data, yf_data, ibapi_data)
    fdb_data = load_and_prepare_data(fdb_path, 'Date', 'Volume')
    yf_data = load_and_prepare_data(yf_path, 'Date', 'Volume')
    ibapi_data = load_and_prepare_data(ibapi_path, 'Date', 'Volume')

    plot_relative_volumes(fdb_data, yf_data, ibapi_data)