# About

This repository aims to get the financial data of publicly listed companies in Indonesia 🇮🇩 for free. It includes reference data (e.g. company profiles, organization structures, etc), daily trading summary (e.g. high, low, bid, ask, foreign buy/sell, etc), and financial statements (balance sheet, profit/loss, and cash flow). This repository is automatically updated daily so you can just chill and relax 😎 🏖 🥥 🌴 🍻.

TL;DR: if you don't want to run this locally and just want to go straight to the data, you can proceed as follows:

|file_name|description|
|-|-|
|[anakperusahaan.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/anakperusahaan.csv)|A list of subsidiaries for each listed company|
|[bondsandsukuk.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/bondsandsukuk.csv)|A list of bonds for each listed company|
|[direktur.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/direktur.csv)|A list of directors for each listed company|
|[dividen.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/dividen.csv)|Dividends information for each listed company|
|financial_statement${YEAR}${QUARTER}.csv|Quarterly financial statement which comprises of balance sheet, profit and loss, and cash flow statements.|
|[issuedbond.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/issuedbond.csv)|Issued bonds for each listed company|
|[kap.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/kap.csv)|A list of auditors for each listed company|
|[komisaris.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/komisaris.csv)|A list of commissioners for each listed company|
|[komiteaudit.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/komiteaudit.csv)|A list of audit committees for each listed company|
|[listed-company.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/listed-company.csv)|Publicly listed companies in Indonesia Stock Exchange|
|[pemegangsaham.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/pemegangsaham.csv)|A list of shareholders for each listed company|
|[profiles.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/profiles.csv)|Company profiles|
|[sekretaris.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/sekretaris.csv)|A list of secretaries for each listed companies|
|[trading-summary.csv](https://raw.githubusercontent.com/ledwindra/indonesia-stock-exchange/main/data/trading-summary.csv)|Daily trading summary since January 2, 2015 (prior that the data is unavailable)|

# Permission
How can we be sure that it's totally okay to get the data from the website? Open [<strong>`its robots.txt site`</strong>](https://idx.co.id/robots.txt) and see the following result:

```
Server Error

404 - File or directory not found.
The resource you are looking for might have been removed, had its name changed, or is temporarily unavailable.
```

It doesn't seem that they care whether or not we scrape their data. 😃

# Clone
Cloning this repository to your local machine is as easy as A-B-C. Just do the following on terminal:

```bash
git clone https://github.com/ledwindra/indonesia-stock-exchange.git
cd indonesia-stock-exchange/
```

# Virtual environment and dependencies
Run the following on terminal if you don't want to mess around with existing modules installed on your machine:

```bash
python -m venv [VIRTUAL-ENVIRONMENT-NAME] # can be anything. for example .venv
source [VIRTUAL-ENVIRONMENT-NAME]/bin/activate
python -m pip install -r requirements.txt
```

To exit from the virtual environment, run `deactivate`.

# End
Hope you enjoy this. Thanks for reading! :smile:
