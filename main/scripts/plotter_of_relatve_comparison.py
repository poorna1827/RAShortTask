import pandas as pd
import matplotlib.pyplot as plt



def load_and_adjust_data(filepath, date_column, expected_format=None, volume_factor=1):
    # Load data
    data = pd.read_csv(filepath)
    # Normalize column names
    data.columns = [col.strip().title() for col in data.columns]
    # Ensure 'Volume' column is numeric
    volume_cols = [col for col in data.columns if 'volume' in col.lower()]
    if volume_cols:
        data.rename(columns={volume_cols[0]: 'Volume'}, inplace=True)
    data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce').fillna(0) * volume_factor
    # Convert date to datetime
    if expected_format:
        try:
            data[date_column] = pd.to_datetime(data[date_column], format=expected_format)
        except ValueError:
            data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
    else:
        data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
    return data


def plot_relative_volumes(fdb_data, yf_data, ibapi_data):
    # Create a new DataFrame for plotting
    df = pd.DataFrame()
    df['Date'] = yf_data['Date']
    df['YF'] = 1  # Yahoo Finance is the baseline, so it's always 1
    df['FDB'] = fdb_data['Volume'] / yf_data['Volume']
    df['IBAPI'] = (ibapi_data['Volume'] * 100) / yf_data['Volume']  # Scaling IBAPI by 100

    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(df['Date'], df['YF'], label='Yahoo Finance (Baseline)', color='red', linewidth=2, linestyle='--')
    plt.plot(df['Date'], df['FDB'], label='Finance Database Relative to YF', color='blue', linewidth=2, linestyle='-')
    plt.plot(df['Date'], df['IBAPI'], label='Interactive Brokers Relative to YF', color='black', linewidth=2,
             linestyle='-')

    plt.title('Relative Volume of FDB and IBAPI to Yahoo Finance for Amazon', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Relative Volume', fontsize=14)
    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True)
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
if __name__ == '__main__':
    fdb_path = 'C:/FinTech/mini_wt/yz_data/financedatabase_daily/AMZN.csv'
    yf_path = 'C:/FinTech/mini_wt/yz_data/yahoo_finance_daily/AMZN_daily_data_from_yf.csv'
    ibapi_path = 'C:/FinTech/mini_wt/yz_data/ibapi_daily/AMZN_daily_data_from_ibapi.csv'

    fdb_data = load_and_adjust_data(fdb_path, 'Date', '%m/%d/%Y')
    yf_data = load_and_adjust_data(yf_path, 'Date', '%Y-%m-%d')
    ibapi_data = load_and_adjust_data(ibapi_path, 'Date', '%Y%m%d')

    plot_relative_volumes(fdb_data, yf_data, ibapi_data)