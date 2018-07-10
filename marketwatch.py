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
    def __init__(self, cash, holdings):
        self.cash = cash
        self.holdings = holdings


f = open('game_info.json', 'r')
game_info = json.load(f)
session = Session(**game_info)

def make_request(method, url, cookies, headers=None, data=None):
    if method == 'POST':
        r  = requests.post(url, headers=headers, cookies=cookies, data=data, proxies={'https': 'https://127.0.0.1:8080'}, verify=False)
    elif method == 'GET':
        r  = requests.get(url, headers=headers, cookies=cookies, data=data, proxies={'https': 'https://127.0.0.1:8080'}, verify=False)
    if r.status_code != 200:
        raise Exception('Bad request: Error Code: {}, method={}, url={}, data={}, headers={}\n{}'.format(r.status_code, method, url, data, session, r.text))
    return r.text

def submit_order(ticker, order_type, shares, term):
    url = session.game_url + '/trade/submitorder'
    headers = {'content-type': 'application/json'}
    data = [{'Fuid':ticker, 'Shares':str(shares), 'Type':order_type, 'Term':term}]
    data = json.dumps(data)
    resp = make_request('POST', url, session.cookies(), headers, data)

def raw_portfolio_page():
    url = session.game_url + '/portfolio'
    return make_request('GET', url, session.cookies())

def get_portfolio():
    html = raw_portfolio_page()
    soup = BeautifulSoup(html, 'html.parser')

    # Find cash
    cash = None
    items = soup.find_all('li', class_='kv__item')
    for item in items:
        if item.find_next('span').string == 'Cash Remaining':
            cash_span = item.find_next('span', class_='kv__value kv__primary')
            cash = float(re.sub('[^0-9\.]', '', cash_span.string))
            break

    # Find holdings
    holdings = {}
    holdings_table = soup.find('div', class_='element element--table holdings')
    print(holdings_table)

    return Portfolio(cash, holdings)
