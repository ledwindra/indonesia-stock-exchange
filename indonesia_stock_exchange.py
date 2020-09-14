import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from random import randint
pd.options.display.max_columns = None
pd.options.mode.chained_assignment = None


def dataframe():
    file_name = sorted(glob.glob('data/trading-*.csv'))
    df = pd.concat([pd.read_csv(x) for x in file_name], sort=False)
    
    return df

def trend(df, min_date='2015-01-01', max_date=date.today().strftime('%Y-%m-%d'), number_ticker=1):
    df = df[(df['Date'] >= min_date) & (df['Date'] <= max_date)]
    df['Date'] = df.apply(lambda x: x['Date'][:10], axis=1).copy()
    df = df.set_index('Date')
    fig, ax = plt.subplots()
    plt.tick_params(axis='both', which='major', labelsize=12)
    ticker = df.StockCode.to_list()
    ticker = [ticker[randint(0, len(ticker))] for i in range(number_ticker)]
    [df[df['StockCode'] == x].Close.plot(figsize=(25, 10), ax=ax) for x in ticker]
    ax.legend(ticker, fontsize=12, loc='upper right')
    plt.title(f'Stock prices of {number_ticker} companies', fontsize=20)
    plt.xlabel('Percentage changes', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    return plt.savefig(f'img/trend-line.png', bbox_inches = 'tight')
    
    
def density(df, number_ticker):
    df['change_percent'] = (df.Close - df.Previous) / df.Close
    fig, ax = plt.subplots()
    plt.tick_params(axis='both', which='major', labelsize=12)
    ticker = df.StockCode.to_list()
    ticker = [ticker[randint(0, len(ticker))] for i in range(number_ticker)]
    [df[df['StockCode'] == x].change_percent.plot(kind='density', figsize=(25, 10), ax=ax) for x in ticker]
    ax.legend(ticker, fontsize=12)
    plt.title(f'Distributions of percentage changes of {number_ticker} companies', fontsize=20)
    plt.xlabel('Percentage changes', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    return plt.savefig(f'img/density.png', bbox_inches = 'tight')
    
def get_close(df, year, date_col, close_col, is_min=True):
    df = df[df['Year'] == year]
    if is_min:
        df = df[df['Date'] == min(df.Date)]
    else:
        df = df[df['Date'] == max(df.Date)]
    df = df[['StockCode', 'Date', 'Close']]
    df = df.rename(columns = {'Date': date_col, 'Close': close_col})
    
    return df

def get_ytd(df):
    min_date = get_close(df, 2020, 'DateMin', 'CloseMin')
    max_date = get_close(df, 2020, 'DateMax', 'CloseMax', is_min=False)
    ytd = pd.merge(min_date, max_date, how='inner', on='StockCode')
    ytd['ytd'] = (ytd.CloseMax - ytd.CloseMin) / ytd.CloseMin
    
    return ytd

def histogram():
    get_ytd(dataframe()).ytd.plot(kind='hist', bins=100, figsize=(25, 10), title='Distributions of Year to Date Values', color='gray')
    return plt.savefig(f'img/histogram.png', bbox_inches = 'tight')

def bar(df):
    ytd = get_ytd(df)
    func_ytd = lambda df, asc: df.sort_values(by='ytd', ascending=asc)[:25]
    ytd = pd.concat([func_ytd(ytd, True), func_ytd(ytd, False)])
    ytd = ytd.sort_values(by='ytd', ascending=True)
    ytd = ytd[['StockCode', 'ytd']]
    ytd['positive'] = ytd.ytd > 0
    ytd.plot(
        x='StockCode',
        y='ytd', kind='bar',
        color=ytd.positive.map({True: 'g', False: 'r'}),
        figsize=(25, 10),
        legend=False,
        title='Companies with Lowest and Highest Year to Date Values'
    )
    return plt.savefig(f'img/bar.png', bbox_inches = 'tight')
    
if __name__ == '__main__':
    histogram()
    trend(dataframe(), min_date='2020-01-01', number_ticker=5)
    density(dataframe(), 5)
    bar(dataframe())