import json
import time
from datetime import datetime

import numpy as np
import requests
from KeyUpdater import headers
from sklearn.linear_model import LinearRegression
def settings():
    settings = {
        'unit':'fastasfuckboii',
        'interval':10,
        'symbol': 'TSLA'
    }
    return settings

def algorithm(data):
    model = LinearRegression()
    X = [x for x in range(len(data))]
    model.fit(X,data)
    trend = model.coef_
    print(trend)
    entry_order_id = ''
    entry_price = np.median(data)
    if trend >= 0:
        payload = {
            "AccountID": "SIM1145924M",
            "TimeInForce": {
                "Duration": "GTC"
            },
            "Quantity": "100",
            "OrderType": "Limit",
            "Symbol": "TSLA",
            "TradeAction": "Buy",
            "Route": "Intelligent",
            "LimitPrice": str(entry_price)
        }
    else:
        payload = {
            "AccountID": "SIM1145924M",
            "TimeInForce": {
                "Duration": "GTC"
            },
            "Quantity": "100",
            "OrderType": "Limit",
            "Symbol": "TSLA",
            "TradeAction": "SellShort",
            "Route": "Intelligent",
            "LimitPrice": str(entry_price)
        }
    url = "https://sim-api.tradestation.com/v3/orderexecution/order"
    response = requests.request("POST", url, json=payload, headers=headers())
    entry_order_id = response.json()['Orders'][0]['OrderID']

    url = f"https://api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/{entry_order_id}"

    response = requests.request("GET", url, headers=headers(), stream=True)
    timelimit = datetime.now()
    for line in response.iter_lines():
        if line:
            line = json.loads(line)
            if (datetime.now() - timelimit).total_seconds() > 10:
                url = f"https://sim-api.tradestation.com/v3/orderexecution/orders/{entry_order_id}"
                requests.request("DELETE", url, headers=headers)
                time.sleep(.5)
                url = f"https://api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{entry_order_id}"
                response = requests.request("GET", url, headers=headers(),stream=True)
                if response.json()['Orders'][0]['Status'] == 'OUT':
                    return
                elif response.json()['Orders'][0]['Status'] == 'FLL':
                    line = json.loads(line)
            if line['Status'] == 'FLL':
                break
    url = "https://api.tradestation.com/v3/marketdata/quotes/TSLA"
    response = requests.request("GET", url, headers=headers())
    diff = float(response.json()['Quotes'][0]['Ask']) - float(response.json()['Quotes'][0]['Bid'])
    if response.json()['Orders'][0]['Message'].count('Buy') == 1:
        payload = {
                    "Type": "OCO",
                    "Orders": [
                        {
                            "AccountID": "SIM1145924M",
                            "TimeInForce": {
                                "Duration": "GTC"
                            },
                            "Quantity": "100",
                            "OrderType": "Limit",
                            "Symbol": "TSLA",
                            "TradeAction": "Sell",
                            "Route": "Intelligent",
                            "LimitPrice": str(round(entry_price+.01,2))
                        },
                        {
                            "AccountID": "SIM1145924M",
                            "TimeInForce": {
                                "Duration": "GTC"
                            },
                            "Quantity": "100",
                            "OrderType": "StopMarket",
                            "Symbol": "TSLA",
                            "TradeAction": "Sell",
                            "Route": "Intelligent",
                            "StopPrice": str(round(entry_price-diff,2))
                        }
                    ]
                }
    else:
        payload = {
            "Type": "OCO",
            "Orders": [
                {
                    "AccountID": "SIM1145924M",
                    "TimeInForce": {
                        "Duration": "GTC"
                    },
                    "Quantity": "100",
                    "OrderType": "Limit",
                    "Symbol": "TSLA",
                    "TradeAction": "BuyToCover",
                    "Route": "Intelligent",
                    "LimitPrice": str(round(entry_price - .01, 2))
                },
                {
                    "AccountID": "SIM1145924M",
                    "TimeInForce": {
                        "Duration": "GTC"
                    },
                    "Quantity": "100",
                    "OrderType": "StopMarket",
                    "Symbol": "TSLA",
                    "TradeAction": "BuyToCover",
                    "Route": "Intelligent",
                    "StopPrice": str(round(entry_price + diff, 2))
                }
            ]
        }
    url = "https://sim-api.tradestation.com/v3/orderexecution/ordergroups"
    response = requests.request("POST", url,json=payload, headers=headers())
    profit_order_id = response.json()['Orders'][0]['OrderID']
    stoploss_order_id = response.json()['Orders'][0]['OrderID']
    return {'Entry':entry_order_id, 'Profit':profit_order_id, 'StopLoss':stoploss_order_id}



if __name__ == '__main__':


    # u can either to a buy or sell short so lets apply a linear regression to see what the direction of the market is
    algorithm([270.50,270.60])
    # sellprofit,  sellstop, buyentry, buystop, buyprofit