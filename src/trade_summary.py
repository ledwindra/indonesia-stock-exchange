import pandas as pd
import requests
from datetime import date, timedelta

def main():
    length = pd.read_csv('./data/listed-company.csv')
    length = len(length)
    initial_day = date(2015, 1, 1)
    today = date.today()
    data = []
    while initial_day <= today:
        day_str = initial_day.strftime('%Y-%m-%d')
        print(day_str, end='\r')
        url = f'https://idx.co.id/umbraco/Surface/TradingSummary/GetStockSummary?date={day_str}&start=0&length={length}'
        status_code = None
        while status_code != 200:
            try:
                response = requests.get(url)
                status_code = response.status_code
                df = response.json()
                df = df['data']
                df = pd.DataFrame(df)
                data.append(df)
            except Exception:
                continue
        initial_day += timedelta(days=1)
    df = pd.concat(data)
    df['Year'] = df.apply(lambda x: x['Date'][:4], axis=1)
    year = set(df.Year.to_list())
    file_name = 'data/trading-summary'
    [df[df['Year'] == x].to_csv(f'{file_name}-{x}.csv', index=False) for x in year]

if __name__ == "__main__":
    main()
