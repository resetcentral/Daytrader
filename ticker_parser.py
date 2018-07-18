#!/usr/bin/python3
import os
import marketwatch

if __name__ == '__main__':
    f = open('new_tickers.txt', 'r')
    tickers = [line.strip() for line in f.readlines()]
    f.close()

    f = open('tickers.txt', 'a')
    for ticker in tickers:
        print(ticker)
        ticker_info = marketwatch.get_ticker_info(ticker)
        f.write(ticker_info + '\n')
    f.close()

    os.system('sort < tickers.txt > tickers_sorted.txt')
    os.system('mv tickers_sorted.txt tickers.txt')
