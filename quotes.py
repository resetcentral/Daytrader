"""
Looks up minute-specific quotes for stock tickers
"""
import requests
import json
import time
import datetime
apikey = None

def load_apikey():
    global apikey
    f = open('aa_api.key', 'r')
    apikey = f.read().strip()
    f.close()

def get_quote_data(ticker):
    if apikey == None:
        load_apikey()

    params = {'function': 'TIME_SERIES_INTRADAY',
              'symbol': ticker,
              'interval': '1min',
              'outputsize': 'full',
              'datatype': 'json',
              'apikey': apikey}
    resp = requests.get('https://www.alphavantage.co/query', params=params)
    resp.raise_for_status()
    quote_data = json.loads(resp.text)
    if 'Error Message' in quote_data:
        if 'Invalid API call' in quote_data['Error Message']:
            return get_quote_data(ticker)
        else:
            raise Exception('Quote Error: {}, {}'.format(ticker, quote_data['Error Message']))
    elif 'Information' in quote_data:
        print('Call limit reached. Sleeping...')
        m = datetime.datetime.now().minute
        n = datetime.datetime.now().minute
        while n == m:
            time.sleep(1)
            n = datetime.datetime.now().minute
        return get_quote_data(ticker)
    return quote_data

def get_price_volume_data(ticker):
    quote_data = get_quote_data(ticker)
    quote_data = quote_data['Time Series (1min)']
    price_volume_data = {}
    for time,data in quote_data.items():
        price_volume_data[time] = {'price':data['1. open'], 'volume':data['5. volume']}
    return price_volume_data
