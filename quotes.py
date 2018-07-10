"""
Looks up minute-specific quotes for stock tickers
"""
import requests
import json
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
    return json.loads(resp.text)

def get_price_data(ticker):
    quote_data = get_quote_data(ticker)
    quote_data = quote_data['Time Series (1min)']
    price_data = {}
    for time,data in quote_data.items():
        price_data[time] = data['1. open']
