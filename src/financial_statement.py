import argparse
import itertools
import os
import pandas as pd
import requests
import string
from datetime import date
from functools import reduce
from multiprocessing import Pool, cpu_count

class FinancialStatement:
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=str, default=date.today().year - 1, help='Financial statement year. Default: last year.', metavar='')
    parser.add_argument('-a', '--audit', type=str, choices=['TW1', 'TW2', 'TW3', 'Audit'], default='Audit', help='''An indication whether it\'s an audited financial statement or not. Q1, ..., Q3 should be put as TW1, ..., TW3, and Q4 should be Audit.''', metavar='')
    parser.add_argument('-q', '--quarter', type=str, choices=['I', 'II', 'III', 'Tahunan'], default='Tahunan', help='''Financial statement quarter. Q1, ..., Q3 should be put as I, ..., III, and Q4 should be Tahunan.''', metavar='')
    args = parser.parse_args()

    def __init__(self):
        self.year = self.args.year
        self.audit = self.args.audit
        self.quarter = self.args.quarter
        
    def download(self, ticker, year, audit, quarter):
        url = f'http://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan%20Keuangan%20Tahun%20{year}/{audit}/{ticker}/FinancialStatement-{year}-{quarter}-{ticker}.xlsx'
        excel_file = f'{ticker}{self.year}{self.audit}{self.quarter}.xlsx'
        try:
            os.system(f'wget {url} -O tmp/{excel_file}')
            return pd.read_excel(f'tmp/{excel_file}')
        except ValueError:
            os.system(f'rm tmp/{excel_file}')
        
    def dataframe(self, ticker, year, audit, quarter, column, sheet):
        try:
            df = pd.read_excel(f'./tmp/{ticker}{year}{audit}{quarter}.xlsx', sheet)
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
        except Exception:
            pass

    def merge(self, ticker, year, audit, quarter):
        year, audit, quarter = self.year, self.audit, self.quarter
        general_info = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 2', 'Unnamed: 1'], 1)
        balance_sheet = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 2)
        profit_loss = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 3)
        cash_flow = self.dataframe(ticker, year, audit, quarter, ['Unnamed: 3', 'Unnamed: 1'], 6)
        merge_multiple = lambda left, right: pd.merge(left, right, how='inner', on='ticker')
        
        try:
            return reduce(merge_multiple, [general_info, balance_sheet, profit_loss, cash_flow])
        except TypeError:
            pass
        
def main(ticker):
    fs = FinancialStatement()
    year, audit, quarter = fs.year, fs.audit, fs.quarter
    file_name = f'data/financial-statement/{ticker}-{fs.year}-{fs.quarter}.json'
    if not os.path.exists(file_name):
        fs.download(ticker, year, audit, quarter)
        data = fs.merge(ticker, fs.year, fs.audit, fs.quarter)
        try:
            data.to_json(file_name, orient='records', indent=4)
        except AttributeError:
            pass
    
if __name__ == '__main__':
    data = [x for x in string.ascii_uppercase]
    data = list(itertools.permutations(data, 4))
    data = [''.join(data[x]) for x in range(len(data))]
    with Pool(cpu_count()) as p:
        p.map(main, data)
