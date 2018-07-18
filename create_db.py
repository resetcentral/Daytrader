#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('price_volume.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS stocks')
c.execute(('CREATE TABLE stocks '
            '(exchange text, ticker text, momentum real, risk real, price real, volume int)'))
c.execute('DROP TABLE IF EXISTS price_volume')
c.execute(('CREATE TABLE price_volume '
            '(ticker text, time text, price real, volume int)'))

f = open('tickers.txt', 'r')
stocks = [line.strip().split(',') for line in f.readlines()]
for stock in stocks:
    exchange, ticker = stock
    c.execute('INSERT INTO stocks VALUES (?, ?, NULL, NULL, NULL, NULL)', (exchange, ticker))

conn.commit()
conn.close()
