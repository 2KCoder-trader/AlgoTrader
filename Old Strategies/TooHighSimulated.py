import time
import requests
from datetime import datetime, timedelta
from KeyUpdater import headers
import json
import pandas_market_calendars as mcal
import pytz
import datetime as dt
from IPython.display import clear_output


def market_status():
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=str(dt.date.today()), end_date=str(dt.date.today()))
    if schedule.empty:
        return False
    else:
        if (schedule['market_open'][0] + timedelta(minutes=2, seconds=1)) > datetime.now(pytz.utc):
            return False
        elif (schedule['market_open'][0] + timedelta(hours=2, minutes=30)) < datetime.now(pytz.utc):
            return False
        else:
            return True


def indicator(tick):
    while market_status():
        data_url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}"
        params = {
            "interval": 1,
            "unit": "Minute",
            "barsback": 3
        }
        while True:
            response = requests.request("GET", data_url, params=params, headers=headers())
            bars = response.json()["Bars"]
            if float(bars[0]["High"]) >= float(bars[1]["High"]):
                date = datetime.strptime(bars[2]["TimeStamp"], "%Y-%m-%dT%H:%M:%SZ")
                while datetime.now(pytz.utc) < datetime(date.year, date.month, date.day, date.hour,
                                                        date.minute) + timedelta(minutes=1):
                    time.sleep(.1)
            else:
                return float(bars[1]["Low"])
    return 0


def set_orders(tick, stop_loss):
    order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    payload = {
        "AccountID": "SIM1145924M",
        "Symbol": tick,
        "Quantity": 1,
        "OrderType": "Market",
        "TradeAction": "BUY",
        "Route": "Intelligent",
        "TimeInForce": {
            "Duration": "GTC"
        }
    }
    response = requests.request("POST", order_url, json=payload, headers=headers())
    time.sleep(5)
    order_id = response.json()["OrderID"]
    url = f"https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{order_id}"

    response = requests.request("GET", url, headers=headers())

    buy_price = response.json()["Legs"][0]["ExecutionPrice"]

    payload = {
        "Type": "BRK",
        "Orders": [
            {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": 1,
                "OrderType": "Limit",
                "TradeAction": "SELL",
                "LimitPrice": buy_price + (buy_price - stop_loss) * 2,
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }},
            {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": 1,
                "OrderType": "StopMarket",
                "StopPrice": stop_loss,
                "TradeAction": "SELL",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
        ]
    }

    return requests.request("POST", order_url, json=payload, headers=headers())


def order_watcher(response):
    profit_order_id = response.json()['Orders'][0]
    loss_order_id = response.json()['Orders'][1]
    url = f"https://api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/{profit_order_id},{loss_order_id}"

    response = requests.request("GET", url, headers=headers(), stream=True)

    for line in response.iter_lines():
        if line:
            for order in json.loads(line):
                if order["Status"] == "FLL":
                    return

if __name__ == '__main__':
    while True:
        trigger_info = indicator("MSFT")
        if trigger_info == 0:
            print(f"Market Closed {datetime.now()}",end="")
            time.sleep(1)
            print("                                ",end="\r")
        else:
            response = set_orders("MSFT", trigger_info[2])
            order_watcher(response)
