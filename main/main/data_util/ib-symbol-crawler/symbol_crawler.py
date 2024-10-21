import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

def fetch_symbols_from_url(url, exch, data):
    resp = requests.get(url)
    if resp.status_code != 200:
        logging.warning(f'Fetch {url} failed. Status code: {resp.status_code}')
        return

    soup = BeautifulSoup(resp.content, 'lxml')
    for table in soup.find_all('table'):
        header = table.find('thead').find('tr')
        column_name = header.find('th').text.strip()
        if column_name.upper() == 'IB SYMBOL':
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [col.text.strip() for col in cols]
                if cols[0] in data:
                    data[cols[0]][-1].append(exch)
                else:
                    data[cols[0]] = cols + [[exch]]
            break

def fetch_num_pages_from_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        logging.warning(f'Fetch {url} failed. Status code: {resp.status_code}')
        return 0

    soup = BeautifulSoup(resp.content, 'lxml')
    ul = soup.find('ul', attrs={'class': 'pagination'})
    return int(ul.find_all('li')[-2].text)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    data = {}
    for exch in ['nasdaq', 'island', 'nyse', 'amex', 'arca']:
        exch_url = f"https://www.interactivebrokers.com/en/index.php?f=2222&exch={exch}&showcategories=STK"
        num_pages = fetch_num_pages_from_url(exch_url)
        logging.info(f'{exch} has {num_pages} pages.')
        for page in range(1, num_pages):
            url = exch_url + f"&page={page}"
            logging.info(f'Fetching page {page} on {exch}.')
            fetch_symbols_from_url(url, exch, data)

    symbols = pd.DataFrame(data.values(),
                           columns=['IB symbol', 'product description', 'symbol', 'currency', 'exchange list'])
    symbols.to_csv('symbols.csv', index=False)