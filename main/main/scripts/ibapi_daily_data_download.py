import subprocess
import os


def download_data(ticker_file_path, base_directory, max_days, size):
    with open(ticker_file_path, 'r') as ticker_file:
        tickers = ticker_file.read().splitlines()

    for index, ticker in enumerate(tickers, start=1):
        print(f"Downloading data for ({index}) {ticker}...")
        results = subprocess.run(
            [
                'python', 'C:/FinTech/mini_wt/main/data_util/ib-data-download/download_daily_bars.py',
                '--base-directory', base_directory,
                '--max-days' if max_days else '',
                '--size', size,
                ticker
            ],
            capture_output=True,
            text=True
        )
        print(results.stdout)


if __name__ == '__main__':
    # Path to the file containing the list of tickers
    ticker_file_path = 'C:/FinTech/mini_wt/yz_data/sp_500_ticker_list.txt'

    # Base directory where data will be saved
    base_directory = 'C:/FinTech/mini_wt/yz_data/ibapi_daily'

    # Specify if max-days flag should be used
    max_days = True

    # Bar size, e.g., '1 day'
    size = '1 day'

    download_data(ticker_file_path, base_directory, max_days, size)
