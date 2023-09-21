import requests
from KeyUpdater import headers
while True:
    tick = 'AAPL'
    url = "https://sim-api.tradestation.com/v3/orderexecution/orders"

    payload = {
        "AccountID": "SIM1145924M",
        "Symbol": f"{tick}",
        "Quantity": "10",
        "OrderType": "Market",
        "TradeAction": "SellShort",
        "TimeInForce": {"Duration": "DAY"},
        "Route": "Intelligent"
    }
    response = requests.request("POST", url, json=payload, headers=headers())
    print(response.text)
    payload = {
        "AccountID": "SIM1145924M",
        "Symbol": f"{tick}",
        "Quantity": "10",
        "OrderType": "Market",
        "TradeAction": "BuyToCover",
        "TimeInForce": {"Duration": "DAY"},
        "Route": "Intelligent"
    }
    response = requests.request("POST", url, json=payload, headers=headers())
    print(response.text)