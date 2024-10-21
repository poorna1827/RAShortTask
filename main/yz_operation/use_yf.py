import yfinance as yf
import pandas as pd

def fetch_daily_stock_data(ticker):
    # Fetch historical data for the stock
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")  # Adjust period for different ranges

    # Print the historical data
    print(hist[['Open', 'High', 'Low', 'Close', 'Volume']])


def fetch_intraday_stock_data(ticker, specific_time):
    # Fetch intraday data at 1-minute intervals
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")

    # Filter data around the specific time, e.g., '15:45:00'
    time_data = hist.between_time(start_time=specific_time, end_time=specific_time)

    # Set display options to avoid truncation
    pd.set_option('display.max_columns', None)  # Ensure all columns are shown
    pd.set_option('display.expand_frame_repr', False)  # Prevent DataFrame wrapping
    pd.set_option('display.max_colwidth', None)  # Display full width of columns

    # Print the filtered data
    print(time_data)

# fetch_daily_stock_data('GOOGL')

# Specify the time you are interested in, e.g., '15:45:00' for 3:45 PM
# fetch_intraday_stock_data('GOOGL', '15:45:00')

def fetch_and_save_intraday_stock_data(ticker_file_path, output_file_path, start_time, end_time):
    # Read the list of tickers from a text file
    with open(ticker_file_path, 'r') as file:
        tickers = file.read().splitlines()

    # Create an empty DataFrame to store stock data
    stock_data = pd.DataFrame()

    # Fetch stock data for each ticker at a specific time
    for i, ticker in enumerate(tickers, start=1):
        print(i,", ", ticker)

        try:
            stock = yf.Ticker(ticker)
            # Get intraday data on a 1-minute interval for today
            hist = stock.history(period="1d", interval="1m")

            # Continue only if there is data to process
            if hist.empty:
                print(f"No data found for {ticker}, possibly delisted.")
                continue

            # Convert index to DatetimeIndex if not already
            if not isinstance(hist.index, pd.DatetimeIndex):
                hist.index = pd.to_datetime(hist.index)

            # Filter for the specific time, e.g., '15:45:00'
            specific_time_data = hist.between_time(start_time=start_time, end_time=end_time)

            if not specific_time_data.empty:
                specific_time_data = specific_time_data.assign(Ticker=ticker)  # Assign ticker symbol to the data
                # Append to the main DataFrame using concat
                stock_data = pd.concat([stock_data, specific_time_data])
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Reset index to include the datetime as a regular column
    stock_data.reset_index(inplace=True)

    # Write the DataFrame to a CSV file
    stock_data.to_csv(output_file_path, index=False)

def fetch_and_save_intraday_stock_data_start_to_end(ticker_file_path, output_file_path, start_time, end_time):
    # Read the list of tickers from a text file
    with open(ticker_file_path, 'r') as file:
        tickers = file.read().splitlines()

    # Create an empty DataFrame to store stock data
    aggregated_data = []
    # Fetch stock data for each ticker at a specific time range
    for i, ticker in enumerate(tickers, start=1):
        print(i, ", ", ticker)
        try:
            stock = yf.Ticker(ticker)
            # Get intraday data on a 1-minute interval for today
            hist = stock.history(period="1d", interval="1m")

            if hist.empty:
                print(f"No data found for {ticker}, possibly delisted.")
                continue

            # Filter data between 9:30 AM and 3:45 PM
            filtered_data = hist.between_time(start_time, end_time)

            if not filtered_data.empty:
                # Aggregate the data
                open_price = filtered_data.iloc[0]['Open']
                high_price = filtered_data['High'].max()
                low_price = filtered_data['Low'].min()
                close_price = filtered_data.iloc[-1]['Close']
                total_volume = filtered_data['Volume'].sum()
                # Assuming dividends and stock splits are reported once per day, not intraday
                dividends = hist['Dividends'].sum()
                stock_splits = hist['Stock Splits'].sum()

                # Append aggregated data to the list
                aggregated_data.append({
                    'Ticker': ticker,
                    'Open': open_price,
                    'High': high_price,
                    'Low': low_price,
                    'Close': close_price,
                    'Volume': total_volume,
                    'Dividends': dividends,
                    'Stock Splits': stock_splits
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

        # Convert list to DataFrame
        stock_data = pd.DataFrame(aggregated_data)

    # Write the DataFrame to a CSV file
    stock_data.to_csv(output_file_path, index=False)


# Define file paths
start_time = '09:30:00'
end_time = '16:00:00'
ticker_file_path = 'C:\FinTech\mini_wt\mini_wt_data\sp_500_ticker_list.txt'
output_file_path = 'C:\FinTech\mini_wt\mini_wt_data\stock_data_0930_to_1600_aggregated.csv'

# Call the function
fetch_and_save_intraday_stock_data_start_to_end(ticker_file_path, output_file_path, start_time, end_time)


