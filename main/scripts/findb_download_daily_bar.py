import os
from datetime import datetime, timedelta
from finance_database import Database
from finance_database.utils import symbol_to_yf_symbol
import yfinance as yf

def download_stock_data(tickers, start_date, end_date, output_folder):
    os.makedirs(output_folder, exist_ok=True)  # Ensure the directory exists
    db = Database()

    for ticker in tickers:
        print(f"Downloading data for {ticker}")
        # Convert ticker to Yahoo Finance symbol if necessary
        yf_ticker = symbol_to_yf_symbol(db, ticker, 'stocks', 'USA')
        stock = yf.Ticker(yf_ticker)
        data = stock.history(start=start_date, end=end_date)
        csv_file_path = os.path.join(output_folder, f"{ticker}_daily_data.csv")
        data.to_csv(csv_file_path)

if __name__ == '__main__':
    # Read tickers from a file or list them directly
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB']  # Example tickers, replace with your actual data

    # Define the time period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20*365)  # 20 years back

    # Format dates as strings
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    # Output folder for storing the CSV files
    output_folder = "path_to_your_output_folder"

    download_stock_data(tickers, start_date, end_date, output_folder)
