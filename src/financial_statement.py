import argparse
import os
import pandas as pd
import requests
from datetime import date, datetime
from functools import reduce
from multiprocessing import Pool, Value, cpu_count

class FinancialStatement:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audit', type=str, choices=['TW1', 'TW2', 'TW3', 'Audit'], default='Audit', help='''An indication whether it\'s an audited financial statement or not. Q1, ..., Q3 should be put as TW1, ..., TW3, and Q4 should be Audit.''', metavar='')
    parser.add_argument('-q', '--quarter', type=str, choices=['I', 'II', 'III', 'Tahunan'], default='Tahunan', help='''Financial statement quarter. Q1, ..., Q3 should be put as I, ..., III, and Q4 should be Tahunan.''', metavar='')
    parser.add_argument('-y', '--year', type=str, default=date.today().year - 1, help='Financial statement year. Default: last year.', metavar='')
    args = parser.parse_args()
    user_agent = os.getenv("USER_AGENT")
    cookie = os.getenv("COOKIE")

    def __init__(self):
        self.audit = self.args.audit
        self.quarter = self.args.quarter
        self.year = self.args.year
        self.headers = {"User-Agent": self.user_agent, "Cookie": self.cookie}
        
    def download(self, ticker, year, audit, quarter):
        status_code = None
        while status_code != 200:
            url = f'https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan%20Keuangan%20Tahun%20{year}/{audit}/{ticker}/FinancialStatement-{year}-{quarter}-{ticker}.xlsx'
            try:
                res = requests.get(url, timeout=None, headers=self.headers)
                status_code = res.status_code
                content = res.content
                return content
            except requests.exceptions.ConnectionError:
                return None
            except requests.exceptions.ReadTimeout:
                return None
        
    def dataframe(self, ticker, year, audit, quarter, column, sheet, content):
        try:
            df = pd.read_excel(content, sheet)
            df = df[column]
            df = df.transpose()
            columns = [str(x).replace(' ', '_').lower() for x in df.iloc[0].to_list()]
            df.columns = [x for x in columns]
            df = df.drop(columns=['nan'])
            df = df.iloc[1:]
            df = df.reset_index(drop=True)
            df['ticker'] = ticker
            ticker = df.pop('ticker')
            df.insert(0, 'ticker', ticker)
            df = df.loc[:,~df.columns.duplicated()]
            return df
        except ValueError:
            pass

    def merge(self, ticker, year, audit, quarter, content):
        year, audit, quarter = self.year, self.audit, self.quarter
        general_info = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 2', 'Unnamed: 1'], 1, content)
        balance_sheet = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 2, content)
        profit_loss = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 3, content)
        cash_flow = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 6, content)
        merge_multiple = lambda left, right: pd.merge(left, right, how='inner', on='ticker')
        try:
            df = reduce(merge_multiple, [general_info, balance_sheet, profit_loss, cash_flow])
            return df
        except TypeError:
            pass
        except ValueError:
            pass
        
def main(ticker):
    fs = FinancialStatement()
    year, audit, quarter = fs.year, fs.audit, fs.quarter
    file_name = f'data/financial-statement/{ticker}-{fs.year}-{fs.quarter}.json'
    if not os.path.exists(file_name):
        content = fs.download(ticker, year, audit, quarter)
        data = fs.merge(ticker, fs.year, fs.audit, fs.quarter, content)
        try:
            data.to_json(file_name, orient='records', indent=4)
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M%S')
            print(f"{current_timestamp}: {ticker} has been saved.")
        except AttributeError:
            pass
    
if __name__ == '__main__':
    listed_company = pd.read_csv('data/reference/listed-company.csv')
    listed_company = listed_company.KodeEmiten.to_list()
    with Pool(cpu_count()) as p:
        p.map(main, listed_company)
