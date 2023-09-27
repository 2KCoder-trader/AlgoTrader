import json
import requests
from KeyUpdater import headers

def settings():
    return {'unit' : 'urownthing','symbol' : 'TSLA'}
def algorithm():
    sym = settings()['symbol']
    url = f"https://api.tradestation.com/v3/marketdata/stream/quotes/{sym}"
    response = requests.request("GET", url, headers=headers(), stream=True)
    for line in response.iter_lines():
        if line:
            line = json.loads(line)
            print(line)
            if 'Error' in line:
                continue
            try:
                ask = float(line['Ask'])
                bid = float(line['Bid'])
            except Exception:
                continue
            url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
            payload = {
                  "AccountID": "SIM1145924M",
                  "Symbol": f"{sym}",
                  "Quantity": "100",
                  "OrderType": "Limit",
                  "TradeAction": "SellShort",
                  "LimitPrice": str(ask),
                  "Route": "Intelligent",
                  "TimeInForce": {
                    "Duration": "GTC"
                  }
            }
            response = requests.request("POST", url, json=payload, headers=headers())
            print(response.json())
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": f"{sym}",
                "Quantity": "100",
                "OrderType": "Limit",
                "TradeAction": "BuytoCover",
                "LimitPrice": str(bid),
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
            while True:
                response = requests.request("POST", url, json=payload, headers=headers())
                if 'Error' in response.json():
                    continue
                else:
                    break



            # return {'Entry': response.json()['Orders'][0], 'Profit': response.json()['Orders'][1], 'StopLoss': response.json()['Orders'][1]}
if __name__ == '__main__':
    algorithm()

