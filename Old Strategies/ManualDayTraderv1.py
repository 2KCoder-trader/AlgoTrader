import time
import pytz
import requests
import pandas_market_calendars as mcal
from KeyUpdater import headers
import datetime as dt
from datetime import datetime, timedelta

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
def send_order(tick,quantity,profit_price,stop_loss):
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
    response = requests.request("POST", order_url, json=payload, headers=headers())
    # time.sleep(5)
    # print(response.json())
    # order_id = response.json()['Orders'][0]["OrderID"]
    # url = f"https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{order_id}"
    #
    # response = requests.request("GET", url, headers=headers())
    # print(response.json())
    # buy_price = response.json()['Orders'][0]["Legs"][0]["ExecutionPrice"]
    order_url = "https://api.tradestation.com/v3/orderexecution/ordergroups"
    payload = {
        "Type": "BRK",
        "Orders": [
            {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": str(quantity),
                "OrderType": "Limit",
                "TradeAction": "SELL",
                "LimitPrice": str(profit_price),
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }},
            {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": str(quantity),
                "OrderType": "StopLimit",
                "StopPrice": str(stop_loss),
                "TradeAction": "SELL",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
        ]
    }

    response = requests.request("POST", order_url, json=payload, headers=headers())
    print(response.json())
    return
if __name__ == '__main__':
    while True:
        if market_status():
            send_order('AVTX',500,.15,.11)
            break
        else:
            time.sleep(1)
    print("Finished")

