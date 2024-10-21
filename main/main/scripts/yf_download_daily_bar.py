import yfinance as yf
import os
from datetime import datetime, timedelta

def download_data(tickers, start_date, end_date, output_folder):
    os.makedirs(output_folder, exist_ok=True)  # Ensure the directory exists

    for ticker in tickers:
        print(f"Downloading data for {ticker}")
        data = yf.download(ticker, start=start_date, end=end_date)
        csv_file_path = os.path.join(output_folder, f"{ticker}_yf.csv")
        data.to_csv(csv_file_path)

if __name__ == '__main__':
    # Read tickers from file
    with open('C:/FinTech/mini_wt/data/sp_500_ticker_list.txt', 'r') as file:
        tickers = file.read().splitlines()

    # Define the time period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20*365)  # Adjust to 20 years back

    # Format dates as strings
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    # Output folder
    output_folder = "C:/FinTech/mini_wt/data/yahoo_finance"

    download_data(tickers, start_date, end_date, output_folder)
