import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count

class TradingData:
    
    def __init__(self, item, base_date, end_date=datetime.now()):
        self.item = item
        self.base_date = base_date
        self.end_date = end_date
    
    def date_range(self):
        i = self.base_date
        date_range = []
        while i <= self.end_date:
            date_range.append(f"data/{self.item}-summary/{self.item}-summary-{i.strftime('%Y-%m-%d')}.json")
            i += timedelta(days=1)
        
        return date_range

    def load_json(self, file_name):
        try:
            return pd.read_json(file_name)
        except ValueError:
            pass

    def read_data(self):
        data = self.date_range()
        with Pool(cpu_count()) as p:
            data = p.map(self.load_json, data)

        return pd.concat(data, sort=False)
    
    def _index(self):
        index = self.read_data()
        index = index[index['IndexCode'] == 'COMPOSITE']
        index = index.reset_index(drop=True)
        
        return index
    
    def _stock(self):
        stock = self.read_data()
        stock = stock.reset_index(drop=True)
        
        return stock
    
class TradingDataFrame:
    
    def __init__(self, index, stock):
        self.index = index
        self.stock = stock
    
    def _dataframe(self, column):
        df = pd.merge(self.stock, self.index, how='left', on='Date')
        df = df.copy()
        df = df[['Date', 'StockCode', 'IndexCode', f'{column}_x', f'{column}_y']]
        df = df.sort_values(by=['StockCode', 'Date'])
        
        df[f'{column}_x_prev'] = df.groupby('StockCode')[f'{column}_x'].shift(1)
        df[f'{column}_y_prev'] = df.groupby('StockCode')[f'{column}_y'].shift(1)
        df['percent_x'] = (df[f'{column}_x'] - df[f'{column}_x_prev']) / df[f'{column}_x_prev']
        df['percent_y'] = (df[f'{column}_y'] - df[f'{column}_y_prev']) / df[f'{column}_y_prev']
        
        q1 = df['percent_x'].quantile(0.25)
        q3 = df['percent_x'].quantile(0.75)
        iqr = q3 - q1
        
        df = df[~((df['percent_x'] < (q1 - 1.5 * iqr)) | (df['percent_x'] > (q3 + 1.5 * iqr)))]
        
        return df
    
    def _stock_code(self, column):
        stock_code = set(self._dataframe(column).StockCode)
        
        return stock_code
    
class Return:
    
    def __init__(self, df, stock_code):
        self.df = df
        self.stock_code = stock_code
    
    def _get_return(self, x):
        df = self.df
        
        return df[df['StockCode'] == x].dropna(subset=['percent_x', 'percent_y'])
           
    def get_return(self):
        with Pool(cpu_count()) as p:
            ret = p.map(self._get_return, self.stock_code)

        return ret
    
class FundamentalData:
    
    def __init__(self, year=datetime.now().year - 1, quarter='Tahunan'):
        self.year = str(year)
        self.quarter = quarter

    def load_json(self, file_name):
        try:
            df = pd.read_json(file_name)[[
                'ticker',
                'current_period_end_date',
                'total_assets',
                'total_liabilities',
                'total_equity',
                'total_comprehensive_income',
                'total_net_cash_flows_received_from_(used_in)_operating_activities',
                'total_net_cash_flows_received_from_(used_in)_investing_activities',
                'total_net_cash_flows_received_from_(used_in)_financing_activities',
                'total_net_increase_(decrease)_in_cash_and_cash_equivalents'
            ]]
            df = df.rename(columns={
                'total_net_cash_flows_received_from_(used_in)_operating_activities': 'operating_cash_flow',
                'total_net_cash_flows_received_from_(used_in)_investing_activities': 'investing_cash_flow',
                'total_net_cash_flows_received_from_(used_in)_financing_activities': 'financing_cash_flow',
                'total_net_increase_(decrease)_in_cash_and_cash_equivalents': 'net_change_cash_equivalent'
            })
            return df
        except ValueError:
            pass

    def read_data(self):
        directory = 'data/financial-statement/'
        data = [f'{directory}/{x}' for x in os.listdir(directory) if self.year in x and self.quarter in x]
        with Pool(cpu_count()) as p:
            data = p.map(self.load_json, data)

        return pd.concat(data, sort=False).reset_index(drop=True)
    
class FundamentalAnalysis:
    
    def percent_change(self, df, column):
        df = pd.concat(df, sort=False)
        df = df.sort_values(by=['ticker', 'current_period_end_date'], ascending=True)
        df[f'{column}_prev'] = df.groupby('ticker')[column].shift(1)
        df = df[df[f'{column}_prev'].isna() == False]
        df = df[['ticker', column, f'{column}_prev']]
        df['percent_change'] = ((df[column] - df[f'{column}_prev']) / df[f'{column}_prev']) * 100

        return df.sort_values(by='percent_change', ascending=False)
    
class Correlation:
    
    def __init__(self, _return):
        self._return = _return

    def _correlate(self, x):
        try:
            return [x.iloc[0,1], np.corrcoef(x.percent_x, x.percent_y)[0][1]]
        except IndexError:
            pass

    def correlate(self):
        with Pool(cpu_count()) as p:
            corr = p.map(self._correlate, self._return)

        return corr
    
class Covariance:
    
    def __init__(self, _return):
        self._return = _return

    def _covariance(self, x):
        try:
            return [x.iloc[0,1], np.cov(x.percent_x, x.percent_y)[0][1]]
        except IndexError:
            pass

    def covariance(self):
        with Pool(cpu_count()) as p:
            cov = p.map(self._covariance, self._return)

        return cov
