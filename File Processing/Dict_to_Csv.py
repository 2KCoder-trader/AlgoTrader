import pandas as pd
import requests
import json
from KeyUpdater import headers
import yfinance as yf
import math
import numpy as np
from datetime import datetime
def save_data(orders):
    all_order_view_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders"
    iterations = math.ceil(len(orders)/100)
    csv = pd.DataFrame(list(orders['id']),columns=["OrderID"])
    token = ""
    for i in range(iterations):
        params = {
            "pageSize": 100,
            "nextToken":token
        }
        response = requests.request("GET", all_order_view_url,params=params, headers=headers())
        for order in response.json()["Orders"]:
            try:
                index_of_row = (csv[csv['OrderID'] == int(order["OrderID"])].index)
                csv.loc[index_of_row,"BuyOrSell"] = order["Legs"][0]["BuyOrSell"]
                csv.loc[index_of_row,"Status"] = order["Status"]
                try:
                    csv.loc[index_of_row,"ExecutionPrice"] = float(order["Legs"][0]["ExecutionPrice"])
                    csv.loc[index_of_row, "Filled Date Time"] = order["ClosedDateTime"]
                except Exception:
                    csv.loc[index_of_row,"ExecutionPrice"] = np.nan
                    csv.loc[index_of_row, "Filled Date Time"] = np.nan
            except Exception:
                print("Error")
                continue
        try:
            token = response.json()["NextToken"]
        except KeyError:
            break
    datetime.now().date().strftime("%Y-%m-%d")
    date = datetime.now().date().strftime("%Y-%m-%d")
    csv.to_csv(date+"_data.csv")
def data_stats(csv):
    buy_price = 0
    confirmed_profit = 0
    potential_loss = 0
    filled_sell_order_count = 0
    received_sell_order_count = 0
    filled_buy_order_count = 0
    cancelled_buy_order_count = 0
    for i in range(csv.shape[0]):
        order = csv.iloc[i]
        if order["BuyOrSell"] == "Buy":
            if order["Status"] == "OUT":
                cancelled_buy_order_count += 1
                continue
            if order["Status"] == "FLL":
                filled_buy_order_count += 1
                buy_price = order["ExecutionPrice"]
        if order["BuyOrSell"] == "Sell":
            if order["Status"] == "FLL":
                filled_sell_order_count += 1
                confirmed_profit += order["ExecutionPrice"] - buy_price
            if (order["Status"] == "ACK") or (order["Status"] == "DON"):
                received_sell_order_count += 1
                potential_loss += yf.Ticker("MSFT").info["currentPrice"] - buy_price
    print("Confirmed Profit:")
    print(confirmed_profit)
    print("Potential Profit:")
    print(potential_loss)
    print("Filled Sell Orders")
    print(filled_sell_order_count)
    print("Open Sell Orders")
    print(received_sell_order_count)
    print("Filled Buy Orders")
    print(filled_buy_order_count)
    print("Cancelled Buy Orders")
    print(cancelled_buy_order_count)
if __name__ == '__main__':
    save_data(pd.read_csv("../orders.csv").drop(['Unnamed: 0'], axis=1))
    data_stats(pd.read_csv("2023-08-16_data.csv").drop(['Unnamed: 0'], axis=1))
