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

def trend(df, title, min_date='2015-01-01', max_date=date.today().strftime('%Y-%m-%d'), ascending=False):
    # get ticker list
    ytd = get_ytd(df)
    func_ytd = lambda df, asc: df.sort_values(by='ytd', ascending=asc)[:5]
    ticker = func_ytd(ytd, ascending).StockCode.to_list()
    
    # transform
    df = df[(df['Date'] >= min_date) & (df['Date'] <= max_date)]
    df['Date'] = df.apply(lambda x: x['Date'][:10], axis=1).copy()
    df = df.set_index('Date')
    
    # visualize
    fig, ax = plt.subplots()
    plt.tick_params(axis='both', which='major', labelsize=12)
    
    [df[df['StockCode'] == x].Close.plot(figsize=(25, 10), ax=ax) for x in ticker]
    ax.legend(ticker, fontsize=12, loc='upper right')
    plt.title(title, fontsize=20)
    plt.xlabel('Period', fontsize=12)
    plt.ylabel('Price per Share', fontsize=12)
    
    return plt.savefig(f'img/trend-line-ascending-{ascending}.png', bbox_inches = 'tight')
    
    
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
    

def histogram():
    get_ytd(dataframe()).ytd.plot(kind='hist', bins=100, figsize=(25, 10), title='Distributions of Year to Date Values', color='gray')
    
    return plt.savefig(f'img/histogram.png', bbox_inches = 'tight')

def bar(df):
    ytd = get_ytd(df)
    func_ytd = lambda df, asc: df.sort_values(by='ytd', ascending=asc)[:5]
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

def correlation(df):
    df = df.select_dtypes(include=['float64'])
    f = plt.figure(figsize=(25, 10))
    plt.matshow(df.corr(), fignum=f.number)
    plt.xticks(range(df.shape[1]), df.columns, fontsize=12, rotation=90)
    plt.yticks(range(df.shape[1]), df.columns, fontsize=12)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=14)
    plt.title('Correlation Matrix', fontsize=16)
    
    return plt.savefig(f'img/correlation.png', bbox_inches = 'tight')
    
if __name__ == '__main__':
    histogram()
    trend(dataframe(), 'Trends of Stock Prices with Highest YTD', min_date='2020-01-01', ascending=False)
    trend(dataframe(), 'Trends of Stock Prices with Lowest YTD', min_date='2020-01-01', ascending=True)
    density(dataframe(), 5)
    bar(dataframe())
    correlation(dataframe())