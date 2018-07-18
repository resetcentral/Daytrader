#!/usr/bin/python3
import sqlite3
from scipy import stats
from datetime import datetime
import quotes

def clear_price_volume(c):
    c.execute('DELETE FROM price_volume')

def download_price_volume_data(c):
    c.execute('SELECT ticker FROM stocks')
    for row in c.fetchall():
        ticker = row[0]
        print(ticker)
        c.execute('SELECT time FROM price_volume WHERE ticker=?', (ticker,))
        row = c.fetchone()
        if not row is None:
            time = row[0]
            print(time)
            now = datetime.now()
            time = datetime.strptime(time)
            if now.day == time.day:
                continue

        price_volume_data = quotes.get_price_volume_data(ticker)
        data = []
        for time, pv_data in price_volume_data.items():
            data.append((ticker, time, pv_data['price'], pv_data['volume']))
        c.executemany('INSERT INTO price_volume VALUES (?,?,?,?)', data)

def compute_regression(c, ticker):
    c.execute('SELECT price,volume FROM price_volume WHERE ticker=? ORDER BY time', (ticker,))
    pv_data = c.fetchall()
    prices = [row[0] for row in pv_data]
    x = [i for i in range(len(prices))]
    slope, intercept, r, p, stderr = stats.linregress(x, prices)
    mom = slope / prices[-1]
    risk = 1 - r**2
    c.execute('UPDATE stocks SET momentum=?,risk=?,price=?,volume=? WHERE ticker=?', (mom, risk, prices[-1], pv_data[-1][1], ticker))

def compute_regressions(c):
    c.execute('SELECT ticker FROM stocks')
    for row in c.fetchall():
        ticker = row[0]
        compute_regression(c, ticker)

if __name__ == '__main__':
    conn = sqlite3.connect('price_volume.db')
    c = conn.cursor()

    clear_price_volume(c)
    download_price_volume_data(c)
    compute_regressions(c)

    conn.commit()
    conn.close()
