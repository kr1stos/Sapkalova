import requests
import pandas as pd
import datetime as dt
import lxml

pd.set_option('expand_frame_repr', False)
df = pd.read_csv('vacancies_dif_currencies.csv')
df['published'] = pd.to_datetime(df['published_at'], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
date_sort = df.sort_values(by='published').reset_index()
month = list(date_sort.published.dt.strftime('%m/%Y').unique())
x = df.groupby('salary_currency')['salary_currency'].count()
y = x[x > 5000].to_dict()
print(y)
z = ['BYR', 'EUR', 'KZT', 'UAH', 'USD']
data1 = pd.DataFrame(columns=['date'] + z)
for i in range(0, len(month)):
    website = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{month[i]}d=1'
    respond = requests.get(website)
    currency = pd.read_xml(respond.text)
    currency1 = currency.loc[currency['CharCode'].isin(['BYN'] + z)]
    BYR = float(currency1.loc[currency1['CharCode'].isin(['BYR', 'BYN'])]['Value'].values[0].replace(',', '.')) / \
          (currency1.loc[currency1['CharCode'].isin(['BYR', 'BYN'])]['Nominal'].values[0])
    EUR = float(currency1.loc[currency1['CharCode'] == 'EUR']['Value'].values[0].replace(',', '.')) / \
          (currency1.loc[currency1['CharCode'] == 'EUR']['Nominal'].values[0])
    KZT = float(currency1.loc[currency1['CharCode'] == 'KZT']['Value'].values[0].replace(',', '.')) / \
          (currency1.loc[currency1['CharCode'] == 'KZT']['Nominal'].values[0])
    USD = float(currency1.loc[currency1['CharCode'] == 'USD']['Value'].values[0].replace(',', '.')) / \
          (currency1.loc[currency1['CharCode'] == 'USD']['Nominal'].values[0])
    UAH = float(currency1.loc[currency1['CharCode'] == 'UAH']['Value'].values[0].replace(',', '.')) / \
          (currency1.loc[currency1['CharCode'] == 'UAH']['Nominal'].values[0])
    data1.loc[i] = [f'{month[i][3:]}-{month[i][:2]}', BYR, EUR, KZT, UAH, USD]
data1.to_csv('currencies.csv')
print(data1.head())