import time
import yfinance as yf
import requests
from KeyUpdater import headers
import pandas as pd
from datetime import datetime
from IPython.display import clear_output
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)

if __name__ == '__main__':
    file = input('Enter File: ')
    orders = pd.read_csv(file)
    tot_pl = 0
    # 'Entry', 'Profit', 'StopLoss'
    order_pl = 0
    for i in range(len(orders)):
        clear_output(wait=True)
        order = orders.iloc[i]
        url = f"https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{order['Entry']},{order['Profit']},{order['StopLoss']}"
        response = requests.request("GET", url, headers=headers())
        print(response.json())
        order_detail_entry = response.json()['Orders'][0]
        order_detail_profit = response.json()['Orders'][0]
        order_detail_stop = response.json()['Orders'][0]
        quantity = float(order_detail_entry['Legs'][0]['ExecQuantity'])
        exec_price = float(order_detail_entry['Legs'][0]['ExecutionPrice'])
        if order_detail_entry['Status'] != 'FLL':
            continue
        elif order_detail_profit['Status'] == 'FLL':
            order_pl += float(order_detail_profit['Legs'][0]['ExecutionPrice']) - exec_price
        elif order_detail_stop['Status'] == 'FLL':
            order_pl += float(order_detail_stop['Legs'][0]['ExecutionPrice']) - exec_price
        else:
            cur_price = yf.Ticker(order_detail_entry['Legs'][0]['Symbol']).info['currentPrice']
        order_pl *= quantity
        tot_pl += order_pl
        order_pl = 0
        print(file)
        print(order_detail_entry['Legs'][0]['Symbol'])
        print(tot_pl)
        time.sleep(1.2)








