
import argparse
import pandas as pd
import requests

class Reference:

    def __init__(self):
        self.key = args.key

    def listed_company(self):
        url = 'https://www.idx.co.id/umbraco/Surface/Helper/GetEmiten?emitenType=s'
        status_code = None
        while status_code != 200:
            response = requests.get(url)
            status_code = response.status_code
            data = response.json()
            df = pd.DataFrame(data)
            df.to_csv('./data/reference/listed-company.csv', index=False)
    
    def company_profile(self):
        ticker = pd.read_csv('./data/reference/listed-company.csv')
        ticker = ticker['KodeEmiten'].to_list()
        data = []
        for t in ticker:
            url = f'https://www.idx.co.id/umbraco/Surface/ListedCompany/GetCompanyProfilesDetail?emitenType=&kodeEmiten={t}&language=id-id'
            status_code = None
            while status_code != 200:
                response = requests.get(url)
                status_code = response.status_code
                response = response.json()
                merge = lambda left, right: pd.merge(left, right, how='left', left_index=True, right_index=True)
                df = pd.DataFrame([{'ticker': t}])
                df = merge(df, pd.DataFrame(response[self.key]))
                data.append(df)
        df = pd.concat(data, sort=False)
        df = df.reset_index(drop=True)
        df.to_csv(f'./data/{self.key.lower()}.csv', index=False)
        
def main():
    reference = Reference()
    listed_company = reference.listed_company()
    reference.company_profile()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--key', type=str, choices=['Profiles', 'Sekretaris', 'Direktur', 'Komisaris', 'KomiteAudit', 'PemegangSaham', 'AnakPerusahaan', 'KAP', 'Dividen', 'BondsAndSukuk', 'IssuedBond'], help='Which key reference to use.', metavar='')
    args = parser.parse_args()
    main()
