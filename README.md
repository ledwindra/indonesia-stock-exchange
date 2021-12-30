# Usage

Do the following steps on your terminal:

```
# create virtual environment
python -m venv .venv

# go the virtual environment
source .venv/bin/activate

# update package manager
pip install --upgrade pip

# install required packages
pip install -r requirements.txt
```

```bash
# cookie and user agent are important because the website uses CloudFlare
# otherwise it would return 403 response code
# periodically update cookie value, e.g. every 30 minutes
export COOKIE="__cf_bm=te9V99jnxli.53zh7c5Hn2NOaxbB2Q38EIKsoiouC3E-1640875057-0-AXD7IexUaVgSIRvEFAhPy6yDFB02RmKgZKedM9Vmj7BDEEUO3PIp28z6N33jhsuzNnrn8pHIizdQQSPWNZFPeV4="

export USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
```

```bash
# src/financial_statement.py
python src/financial_statement.py \
    --audit Audit \
    --quarter Tahunan \
    --year 2020

# src/reference.py
python src/reference.py --key Profiles

# src/summary.py
python src/summary.py --day 2021-01-01 \
    --file_name stock-summary \
    --summary GetStockSummary
```
