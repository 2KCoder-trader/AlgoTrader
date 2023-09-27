import json
import time
from datetime import datetime
import yfinance as yf
import numpy as np
import requests
from KeyUpdater import headers
from sklearn.linear_model import LinearRegression
def settings():
    settings = {
        'unit':'fastasfuckboii',
        'barsback':2,
        'symbol': 'TSLA'
    }
    return settings

def algorithm(data):
    model = LinearRegression()
    X = [[x] for x in range(len(data))]
    model.fit(X,data)
    trend = model.coef_
    print(trend)
    # entry_price = round(np.mean(data),2)
    if trend >= 0:
        action = "Buy"
    else:
        action = "SellShort"
    payload = {
        "AccountID": "SIM1145924M",
        "TimeInForce": {
            "Duration": "GTC"
        },
        "Quantity": "100",
        "OrderType": "Market",
        "Symbol": "TSLA",
        "TradeAction": f"{action}",
        "Route": "Intelligent"
    }

    url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
    execute_response = requests.request("POST", url, json=payload, headers=headers())
    print(execute_response.json())
    entry_order_id = execute_response.json()['Orders'][0]['OrderID']

    url = f"https://sim-api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/{entry_order_id}"

    response = requests.request("GET", url, headers=headers(), stream=True)
    timelimit = datetime.now()
    for line in response.iter_lines():
        if line:
            line = json.loads(line)
            print('Waiting',line)
            if (datetime.now() - timelimit).total_seconds() > 5:
                url = f"https://sim-api.tradestation.com/v3/orderexecution/orders/{entry_order_id}"
                requests.request("DELETE", url, headers=headers())
                time.sleep(.5)
                url = f"https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{entry_order_id}"
                response = requests.request("GET", url, headers=headers())
                print("Delete:", response.json())
                if response.json()['Orders'][0]['Status'] == 'OUT':
                    print('OUT')
                    return
                elif response.json()['Orders'][0]['Status'] == 'FLL':
                    line = response.json()['Orders'][0]
            if 'Status' in line:
                pass
            else:
                continue
            if line['Status'] == 'FLL':
                entry_price = float(line['Legs'][0]['ExecutionPrice'])
                print('FLL')
                break
    info = yf.Ticker('TSLA').info
    diff = abs(info['ask'] - info['bid'])
    diff = round(diff,2)
    print(diff)
    if execute_response.json()['Orders'][0]['Message'].count('Buy') == 1:
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
                            "LimitPrice": str(round(entry_price-.01,2)),
                            "StopPrice":str(round(entry_price - diff, 2))

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
                    "LimitPrice": str(round(entry_price + .01, 2)),
                    "StopPrice":str(round(entry_price + diff, 2))

                }
            ]
        }
    url = "https://sim-api.tradestation.com/v3/orderexecution/ordergroups"
    response = requests.request("POST", url,json=payload, headers=headers())
    print(response.json())
    profit_order_id = response.json()['Orders'][0]['OrderID']
    stoploss_order_id = response.json()['Orders'][1]['OrderID']
    url = f"https://sim-api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/{profit_order_id}"
    response = requests.request("GET", url, headers=headers(), stream=True)
    for line in response.iter_lines():
        if line:
            line = json.loads(line)
            print(line)
            if 'Status' in line:
                pass
            else:
                continue
            if line['Status'] == 'OUT':
                print('OUT')
                break
            if line['Status'] == 'FLL':
                print('FLL')
                break
    print(entry_order_id)
    print(profit_order_id)
    print(stoploss_order_id)
    return {'Entry':entry_order_id, 'Profit':profit_order_id, 'StopLoss':stoploss_order_id}



if __name__ == '__main__':
    pass

    # u can either to a buy or sell short so lets apply a linear regression to see what the direction of the market is
    # algorithm([270.50,270.60])
    # sellprofit,  sellstop, buyentry, buystop, buyprofit