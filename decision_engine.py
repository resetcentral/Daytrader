#!/usr/bin/python3
import sqlite3
import sys
import marketwatch

# 9:30AM - 4:00PM = 6H30M
# Buy at 12:00PM (T-2H30M)
# Sell at 4:00PM (T+4H)
HOLD_LEN = 4 * 60
CREDIT_RATE = 0.03 / 365 / HOLD_LEN
DEBT_RATE = 0.06 / 365 / HOLD_LEN
COMMISSION = 10.00 * 2
MIN_PRICE = 2.00
VOL_LIMIT = 0.01

def max_holding(stock_data, cash):
    shares = cash / stock_data['price']
    value = shares * stock_data['price']
    mh = value / cash
    return mh

def adjusted_momentum(stock_data):
    com_adj = COMMISSION / (HOLD_LEN * stock_data['price'])
    adj_mom = abs(stock_data['momentum']) - com_adj
    return adj_mom

def val_weight_ratio(stock_data, cash):
    mh = max_holding(stock_data, cash)
    w = mh * stock_data['risk']
    adj_mom = adjusted_momentum(stock_data)
    v = mh * adj_mom
    return v / w

def solve_knapsack(decision_data, portfolio):
    cash = portfolio.get_cash()

    stock_data_list = [(ticker, stock_data) for ticker,stock_data in decision_data.items()]

    while cash > 0 and len(stock_data_list) > 0:
        stock_data_list.sort(key=lambda si: val_weight_ratio(si[1], cash), reverse=True)
        ticker, stock_data = stock_data_list.pop(0)
        if adjusted_momentum(stock_data) <= CREDIT_RATE:
            break

        mh = max_holding(stock_data, cash)
        shares = int(mh * cash / stock_data['price'])
        print(ticker, shares)
        if shares <= 0:
            break

        print(ticker, stock_data['momentum'])
        if stock_data['momentum'] < 0:
            order_type = 'Short'
        else:
            order_type = 'Buy'
        fuid = '{}-{}'.format(stock_data['exchange'], ticker)
        marketwatch.submit_order(fuid, order_type, shares, 'Day')
        
        cash = portfolio.get_cash(reload=True)

def sell_all_holdings(portfolio, decision_data):
    holdings = portfolio.get_holdings(reload=True)
    for holding in holdings:
        ticker = holding['ticker']
        shares = holding['shares']
        fuid = '{}-{}'.format(decision_data[ticker]['exchange'], ticker)
        if holding['type'] == 'Buy':
            order_type = 'Sell'
        else:
            order_type = 'Cover'

        marketwatch.submit_order(fuid, order_type, shares, 'Day')
        

def get_decision_data():
    conn = sqlite3.connect('price_volume.db')
    c = conn.cursor()
    c.execute('SELECT * FROM stocks')
    decision_data = {}
    for row in c.fetchall():
        exchange, ticker, momentum, risk, price, volume = row
        decision_data[ticker] = {'exchange': exchange, 'momentum':momentum, 'risk':risk, 'price':price, 'volume':volume}
    conn.close()
    return decision_data

def filter_stocks(decision_data):
    remove = []
    for ticker, data in decision_data.items():
        if abs(data['momentum']) <= CREDIT_RATE or data['price'] <= MIN_PRICE: 
            remove.append(ticker)
    for ticker in remove:
        del decision_data[ticker]

if __name__ == '__main__':
    decision_data = get_decision_data()
    portfolio = marketwatch.Portfolio()
    if sys.argv[1] == 'buy':
        filter_stocks(decision_data)
        solve_knapsack(decision_data, portfolio)
    elif sys.argv[1] == 'sell':
        sell_all_holdings(portfolio, decision_data)
