import time
import pandas as pd
import yfinance as yf
import requests
import AlgoSimulated
from KeyUpdater import headers
from datetime import datetime,timedelta
def Idle():
    order_view_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/"
    while True:
        if AlgoSimulated.market_status()[0]:
            orders = pd.read_csv("orders.csv")
            for symbol in orders["Symbol"].unique():
                rec = yf.Ticker(symbol).info["reccomendationKey"]
                if ('hold' == rec) or ('none' == rec) or (
                        'underperform' == rec) or (
                        'sell' == rec):
                    AlgoSimulated.close_positions(symbol)
            time.sleep(3)
            temp = orders["Sell Order"]
            for order in temp:
                response = requests.request("GET", order_view_url + order, headers=headers)
                if (response.json()["Status"] != "ACK") | (response.json()["Status"] != "FPL") | (response.json()["Status"] != "OPN"):
                    i = orders[orders["Sell Order"] == order].index
                    orders.drop(i,axis=0)
                    continue
                time_str = response.json()["OpenedDateTime"]
                open_date = datetime.strptime(time_str[:time_str.indexAt("T")], '%m-%d-%Y').date()
                if datetime.now()> open_date+timedelta(days = 7):
                    d_response = requests.request("DELETE", AlgoSimulated.cancel_order_url + order, headers=headers)
                    print('Delete Order Sent Response: ', d_response.json())
                    sym = response.json()["Legs"][0]["Symbol"]
                    qremain = response.json()["Legs"][0]["QuantityRemaining"]
                    payload = {
                        "AccountID": "SIM1145924M",
                        "Symbol": sym,
                        "Quantity": qremain,
                        "OrderType": "Market",
                        "TradeAction": "SELL",
                        "Route": "Intelligent",
                        "TimeInForce": {
                            "Duration": "GTC"
                        }
                    }
                    response = requests.request("POST", AlgoSimulated.order_url, json=payload, headers= KeyUpdater.headers)

