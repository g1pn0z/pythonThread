#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 22:35:13 2020

@author: rinat
"""
from binance.client import Client
import json
import requests
from tabletext import to_text
import math


api_key = '<api-key>'
secret_key = '<secret-key>'
order_keys = ['symbol', 'price']
min_sell_sum = 0.1
not_sellable = ['BNB', 'USDT']

client = Client(api_key, secret_key)

def my_open_orders():
    # {'symbol': 'WINBNB', 'orderId': 26942754, 'orderListId': -1, 'clientOrderId': 'and_1f3348a69d864169a002afb2b75c1048', 'price': '0.00000961', 'origQty': '67248.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1599449551552, 'updateTime': 1599449551552, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}
    return client.get_open_orders()

def my_balance():
    # [{'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'}]
    return client.get_account().get('balances')

def print_opened_orders():
    print(to_text([order_keys] + [[o[k] for k in order_keys] for o in my_open_orders()]))

def cancel_order(symbol, orderId, **kwargs):
    print(client.cancel_order(symbol=symbol, orderId=orderId))

def sell(symbol, quantity):
    symbol += 'BNB'
    print('sell', symbol, quantity)
    print(client.order_market_sell(symbol=symbol, quantity=quantity))

def cancel_all_orders():
    print('Отменяем все открытые ордера')
    [cancel_order(**order) for order in my_open_orders()]

def sell_everything_except_bnb_and_usdt():
    # sm = lambda item: float(item['free']) + float(item['locked'])
    sm = lambda item: float(item['free'])

    data = [[o['asset'], sm(o)] for o in my_balance() if sm(o) > min_sell_sum and o['asset'] not in not_sellable]
    [sell(*item) for item in data]


def count_balance():
    prices = {item['symbol']: item['price'] for item in client.get_all_tickers()}

    BTC_TO_RUB = float(prices.get('BTCRUB'))
    BTC_TO_USD = float(prices.get('BTCTUSD'))

    def get_price_in_other(balance, coin):
        rub = float(balance) * float(prices.get('{}RUB'.format(coin), 0))
        usd = float(balance) * float(prices.get('{}USDT'.format(coin), 0))
        btc = float(balance) * float(prices.get('{}BTC'.format(coin), 0))

        if btc == 0:
            btc = rub / BTC_TO_RUB if rub else usd / BTC_TO_USD

        if rub == 0:
            if btc != 0:
                rub = btc * BTC_TO_RUB

        if usd == 0:
            if btc != 0:
                usd = btc * BTC_TO_USD

        if btc == 0:
            btc = rub / BTC_TO_RUB if rub else usd / BTC_TO_USD

        return rub, usd, btc

    total_rub, total_usd, total_btc = (0, 0, 0)

    for item in my_balance():
        b = float(item['free']) + float(item['locked'])

        if float(b) > 0:
            rub, usd, btc = get_price_in_other(b, item['asset'])
            total_rub += rub
            total_usd += usd
            total_btc += btc

    print('Всего в rub', total_rub)
    print('Всего в usd', total_usd)
    print('Всего в btc', total_btc)

