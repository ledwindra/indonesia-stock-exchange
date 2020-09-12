import argparse
import os
import pandas as pd
import requests
import xlrd
from functools import reduce

class FinancialStatement:
    
    def __init__(self):
        self.year = args.year
        self.audit = args.audit
        self.quarter = args.quarter
    
    def listed_company(self):
        url = 'https://www.idx.co.id/umbraco/Surface/Helper/GetEmiten?emitenType=s'
        status_code = None
        while status_code != 200:
            response = requests.get(url)
            status_code = response.status_code
            data = response.json()
            df = pd.DataFrame(data)
        
        return df
        
    def download(self, ticker, year, audit, quarter):
        url = f'http://www.idx.co.id/Portals/0/StaticData/ListedCompanies/Corporate_Actions/New_Info_JSX/Jenis_Informasi/01_Laporan_Keuangan/02_Soft_Copy_Laporan_Keuangan//Laporan%20Keuangan%20Tahun%20{year}/{audit}/{ticker}/FinancialStatement-{year}-{quarter}-{ticker}.xlsx'
        try:
            res = requests.get(url, timeout=5)
            status_code = res.status_code
            if not os.path.exists('tmp'):
                os.mkdir('tmp')
            excel = open(f'./tmp/{ticker}{self.year}{self.audit}{self.quarter}.xlsx', 'wb')
            excel.write(res.content)
            return status_code
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.ReadTimeout:
            return None
        
    def dataframe(self, ticker, year, audit, quarter, column, sheet):
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

    def concatenate(self, listed_company, year, audit, quarter, column, sheet):
        data = []
        for ticker in listed_company:
            try:
                data.append(self.dataframe(ticker, year, audit, quarter, column, sheet))
            except FileNotFoundError:
                pass
            except xlrd.XLRDError:
                pass

        df = pd.concat(data, axis='columns')
        df = pd.concat(data, sort=False)
        df = df.reset_index(drop=True)

        return df
        
def main():
    fs = FinancialStatement()
    listed_company = fs.listed_company()['KodeEmiten']
    download = [fs.download(ticker, fs.year, fs.audit, fs.quarter) for ticker in listed_company]
    # concatenate each section in the financial statements
    general_info = fs.concatenate(listed_company, fs.year, fs.audit, fs.quarter, ['Unnamed: 2', 'Unnamed: 1'], 1)
    balance_sheet = fs.concatenate(listed_company, fs.year, fs.audit, fs.quarter, ['Unnamed: 3', 'Unnamed: 1'], 2)
    profit_loss = fs.concatenate(listed_company, fs.year, fs.audit, fs.quarter, ['Unnamed: 3', 'Unnamed: 1'], 3)
    cash_flow = fs.concatenate(listed_company, fs.year, fs.audit, fs.quarter, ['Unnamed: 3', 'Unnamed: 1'], 6)
    # merge dataframes and save to csv based on period
    merge_multiple = lambda left, right: pd.merge(left, right, how='inner', on='ticker')
    df = reduce(merge_multiple, [general_info, balance_sheet, profit_loss, cash_flow])
    df.to_csv(f'./data/financial_statement{fs.year + fs.audit + fs.quarter}.csv', index=False)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-y',
        '--year',
        type=str,
        help='Financial statement year',
        metavar=''
    )
    parser.add_argument(
        '-a',
        '--audit',
        type=str,
        help='''
        An indication whether it\'s an audited financial statement or not.
        Q1, ..., Q3 should be put as TW1, ..., TW3, and Q4 should be Audit.
        ''',
        metavar=''
    )
    parser.add_argument(
        '-q',
        '--quarter',
        type=str,
        help='''
        Financial statement quarter. Q1, ..., Q3 should be put as I,
        ..., III, and Q4 should be Tahunan.''',
        metavar=''
    )
    args = parser.parse_args()
    main()
