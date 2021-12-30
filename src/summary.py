import argparse
import json
import os
import requests
from datetime import date, datetime, timedelta

class Summary:
    def __init__(self):
        self.summary = args.summary
        self.file_name = args.file_name
        self.day = args.day

    def response(self, url, keys):
        status_code = None
        while status_code != 200:
            try:
                response = requests.get(url, headers=headers)
                status_code = response.status_code
                response = response.json()
                response = response[keys]
            except Exception:
                continue

        return response
    
    def to_json(self, data, day_str):
        file_dir = f'data/{self.file_name}/{self.file_name}-{day_str}.json'
        if len(data) > 0:
            with open(file_dir, 'w') as file:
                json.dump(data, file)

def main():
    summary = Summary()
    day = summary.day
    today = date.today()
    while day <= today:
        day_str = day.strftime('%Y-%m-%d')
        url = f'https://idx.co.id/umbraco/Surface/TradingSummary/{summary.summary}?date={day_str}'
        file_dir = f'data/{summary.file_name}/{summary.file_name}-{day_str}.json'
        if not os.path.exists(file_dir):
            record = summary.response(url, 'recordsTotal')
            data = summary.response(f'{url}&start=0&length={record}', 'data')
            summary.to_json(data, day_str)
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%s')
            print(f'{current_timestamp}: market date for the period of {day_str} has been saved')
        day += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--day', type=date.fromisoformat, default=date(2015, 1, 1), help='Starting date — e.g. "2021-12-30"', metavar='')
    parser.add_argument('-f', '--file_name', type=str, choices=['broker-summary', 'index-summary', 'stock-summary'], help='File name which corresponds to information that will be obtaind.', metavar='')
    parser.add_argument('-s', '--summary', type=str, choices=['GetBrokerSummary', 'GetIndexSummary', 'GetStockSummary'], help='Which summary that will be scraped.', metavar='')
    args = parser.parse_args()
    user_agent = os.getenv("USER_AGENT")
    cookie = os.getenv("COOKIE")
    headers = {"User-Agent": user_agent, "Cookie": cookie}
    main()
