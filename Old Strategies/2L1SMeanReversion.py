import time
import json
import requests
from KeyUpdater import headers
from datetime import datetime
import numpy as np
import multiprocessing


def get_price(tick):
    params = {
        "interval": "1",
        "unit": "minute",
        "barsback": "1",
        "lastdate": str(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
    }
    response = requests.request("GET", f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}",
                                params=params, headers=headers())
    return int(response.json()["Orders"][0]['Close'])


def buy_at_price(tick, quantity):
    order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    payload = {
        "AccountID": "SIM1145924F",
        "Symbol": tick,
        "Quantity": str(quantity),
        "OrderType": "Market",
        "TradeAction": "BUY",
        "Route": "Intelligent",
        "TimeInForce": {
            "Duration": "GTC"
        }
    }
    return requests.request("POST", order_url, json=payload, headers=headers())


def sell_at_price(tick, quantity):
    order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    payload = {
        "AccountID": "SIM1145924F",
        "Symbol": tick,
        "Quantity": str(quantity),
        "OrderType": "StopMarket",
        "TradeAction": "SELL",
        "Route": "Intelligent",
        "TimeInForce": {
            "Duration": "GTC"
        }
    }
    return requests.request("POST", order_url, json=payload, headers=headers())


def mean_reversion(tick, low_ma_len, high_ma_len):
    position = False
    low = high = list()
    while True:
        price = get_price(tick)
        if len(low) > low_ma_len:
            low.pop(0)
        if len(high) > high_ma_len:
            high.pop(0)
        low.append(price)
        high.append(price)
        low_ma = np.mean(low)
        high_ma = np.mean(high)
        if (low_ma < high_ma) and not position:
            position = True
            print(buy_at_price(tick, 1))
        if (low_ma > high_ma) and position:
            position = False
            print(sell_at_price(tick, 1))
        time.sleep(60)


if __name__ == '__main__':
    # dont forget to run Key Updater before this
    mean_reversion("CLX23.NYM", 1, 2)
