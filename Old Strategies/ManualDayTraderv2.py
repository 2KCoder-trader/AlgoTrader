import time
import pytz
import requests
import pandas_market_calendars as mcal
import math
import yfinance
import json
import KeyUpdater
from KeyUpdater import headers
import requests
import datetime as dt
from datetime import datetime, timedelta
import multiprocessing

def send_order(tick,balance):
    balance = balance*.90
    quantity = math.floor(balance/yfinance.download(tick,prepost=True)[-1]['Close'])

    order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    payload = {
        "AccountID": "SIM1145924M",
        "Symbol": tick,
        "Quantity": str(quantity),
        "OrderType": "Market",
        "TradeAction": "BUY",
        "Route": "Intelligent",
        "TimeInForce": {
            "Duration": "GTC"
        }
    }
    market_response = requests.request("POST", order_url, json=payload, headers=headers())
    print(market_response)
    market_id = market_response.json()["Orders"][0]["OrderID"]


    url = f"https://api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/{market_id}"

    response = requests.request("GET", url, headers=headers, stream=True)
    buying_price = 0
    for line in response.iter_lines():
        if line:
            try:
                cleaned_line = json.loads(line)
                if cleaned_line['StatusDescription'] == 'Filled':
                    buying_price = float(cleaned_line["Legs"][0]["ExecutionPrice"])
                    break
            except Exception:
                continue

    order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    payload = {
        "AccountID": "SIM1145924M",
        "Symbol": tick,
        "Quantity": str(quantity),
        "OrderType": "Limit",
        "LimitPrice": str(round(buying_price*1.03,2)),
        "TradeAction": "SELL",
        "Route": "Intelligent",
        "TimeInForce": {
            "Duration": "GTC"
        }
    }
    setting_sell_response = requests.request("POST", order_url, json=payload, headers=headers())
    print(setting_sell_response)



if __name__ == '__main__':
    multiprocessing.Process(target = KeyUpdater.access_token)
    time.sleep(1)


    # I cant do a market order may buy at a peak
    # It must wait for it to dip just between the low and the close
    url = "https://api.tradestation.com/v3/brokerage/accounts/17551942/balances"

    response = requests.request("GET", url, headers=headers())
    tick = input("Ticker: ")
    send_order(tick,float(response.json()["Balances"][0]["BuyingPower"]))




