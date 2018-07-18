#!/usr/bin/python3
"""
An API for interacting with a Marketwatch stock exchange simulator.
"""
import requests
import json
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import re

class Session(object):
    def __init__(self, game_url, oidc_token, djcs_route):
        self.game_url = game_url
        self.oidc_token = oidc_token
        self.djcs_route = djcs_route

    def cookies(self):
        return {'oidc_token': self.oidc_token, 'djcs_route': self.djcs_route}


class Portfolio(object):

    def __init__(self):
        self.soup = None
        self.get_cash()
        self.get_holdings()
    
    def load_parser(self):
        html = self.raw_portfolio_page()
        soup = BeautifulSoup(html, 'html.parser')
        self.soup = soup

    def raw_portfolio_page(self):
        url = session.game_url + '/portfolio'
        return make_request('GET', url, session.cookies())

    def get_cash(self, reload=False):
        if self.soup is None or reload:
            self.load_parser()

        buying_power = None
        net_worth = None
        items = self.soup.find_all('li', class_='kv__item')
        for item in items:
            span = item.find_next('span')
            if span.string == 'Net Worth':
                nw_span = item.find_next('span', class_='kv__value kv__primary')
                nw_str = re.sub('[^0-9\.]', '', nw_span.string)
                net_worth = float(nw_str)
            elif span.string == 'Buying Power':
                bp_span = item.find_next('span', class_='kv__value kv__primary')
                bp_str = re.sub('[^0-9\.]', '', bp_span.string)
                buying_power = float(bp_str)
                break
        self.cash = buying_power - net_worth
        return self.cash

    def get_holdings(self, reload=False):
        if self.soup is None or reload:
            self.load_parser()

        holdings = []
        holdings_table = self.soup.find('div', class_='element element--table holdings')
        tbody = holdings_table.find('tbody')
        if tbody is None:
           self.holdings = holdings
           return holdings
        rows = tbody.find_all('tr')
        for row in rows:
            holding = {}
            ticker = row.find_next('mini-quote').string
            shares_str = row.find_next('small').contents[0]
            shares = int(shares_str)
            order_type = row.find_all_next('small')[1].string
            holding = {'ticker': ticker, 'shares': shares, 'type':order_type}
            holdings.append(holding)

        self.holdings = holdings
        return holdings


f = open('game_info.json', 'r')
game_info = json.load(f)
session = Session(**game_info)

def make_request(method, url, cookies=None, headers=None, data=None):
    if method == 'POST':
        r  = requests.post(url, headers=headers, cookies=cookies, data=data, proxies={'https': 'https://127.0.0.1:8080'}, verify=False)
    elif method == 'GET':
        r  = requests.get(url, headers=headers, cookies=cookies, data=data, proxies={'https': 'https://127.0.0.1:8080'}, verify=False)
    if r.status_code != 200:
        raise Exception('Bad request: Error Code: {}, method={}, url={}, data={}, headers={}\n{}'.format(r.status_code, method, url, data, session, r.text))
    return r.text

def submit_order(ticker, order_type, shares, term):
    """
    order_types: 'Buy', 'Sell', 'Short', 'Cover'
    """
    url = session.game_url + '/trade/submitorder'
    headers = {'content-type': 'application/json'}
    data = [{'Fuid':ticker, 'Shares':str(shares), 'Type':order_type, 'Term':term}]
    data = json.dumps(data)
    resp = make_request('POST', url, session.cookies(), headers, data)
    resp_data = json.loads(resp)
    if not resp_data['succeeded']:
        message = resp_data['message']
        if 'trading volume limit' in message:
            shares_allowed = re.match('.*\((.*) shares\).*', message).group(1)
            shares = int(shares_allowed) - 1
            return submit_order(ticker, order_type, shares, term)
    else:
        return shares

def get_ticker_info(ticker):
    url = 'https://www.marketwatch.com/investing/stock/' + ticker
    html = make_request('GET', url)
    soup = BeautifulSoup(html, 'html.parser')
    inst_type = soup.find('meta', attrs={'name':'instrumentType'})['content'].upper()
    if inst_type == 'AMERICANDEPOSITORYRECEIPTSTOCK':
        inst_type = 'ADR'

    exchange = soup.find('meta', attrs={'name':'exchangeIso'})['content']
    return '{}-{},{}'.format(inst_type, exchange, ticker)

if __name__ == '__main__':
    p = Portfolio()
    print(p.holdings)
