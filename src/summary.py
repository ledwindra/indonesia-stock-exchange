import argparse
import pandas as pd
import requests
from datetime import date, timedelta

class Summary:

    def __init__(self):
        self.summary = args.summary
        self.file_name = args.file_name

    def response(self, url, keys):
        status_code = None
        while status_code != 200:
            try:
                response = requests.get(url)
                status_code = response.status_code
                response = response.json()
                response = response[keys]
            except Exception:
                continue

        return response

    def dataframe(self, data):
        df = pd.DataFrame(data)

        return df
    
    def to_csv(self, df):
        df = pd.concat(df)
        df['Year'] = df.apply(lambda x: x['Date'][:4], axis=1)
        year = set(df.Year.to_list())
        file_name = self.file_name

        return [df[df['Year'] == x].to_csv(f'data/{file_name}/{file_name}-{x}.csv', index=False) for x in year]

def main():
    summary = Summary()
    day = date(2015, 1, 1)
    today = date.today()
    df = []
    while day <= today:
        day_str = day.strftime('%Y-%m-%d')
        print(day_str, end='\r')
        url = f'https://idx.co.id/umbraco/Surface/TradingSummary/{summary.summary}?date={day_str}'
        record = summary.response(url, 'recordsTotal')
        data = summary.response(f'{url}&start=0&length={record}', 'data')
        df.append(summary.dataframe(data))
        day += timedelta(days=1)
    summary.to_csv(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--summary',
        type=str,
        choices=['GetBrokerSummary', 'GetIndexSummary', 'GetStockSummary'],
        help='Which summary that will be scraped.',
        metavar=''
    )
    parser.add_argument(
        '-f',
        '--file_name',
        type=str,
        choices=['broker-summary', 'index-summary', 'stock-summary'],
        help='File name which corresponds to information that will be obtaind.',
        metavar=''
    )
    args = parser.parse_args()
    main()
