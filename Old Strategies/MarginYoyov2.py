import time
import numpy as np
import pandas as pd
import pytz
import requests
from KeyUpdater import headers
import json
from datetime import datetime, timedelta
import datetime as dt
import pandas_market_calendars as mcal


def buy_trigger(tick):
    params = {
        "interval":5,
        "unit":"Minute"
    }
    stream_url = f"https://api.tradestation.com/v3/marketdata/stream/barcharts/{tick}"
    response = requests.request("GET", stream_url,params=params, headers=headers(), stream=True)
    skip_line = 0
    prev_close = 0
    action = ""
    for line in response.iter_lines():
        if line:
            if skip_line == 0:
                skip_line = 1
                continue
            loaded_line = json.loads(line)
            try:
                if float(loaded_line['UpVolume']) > float(loaded_line['DownVolume'])+float(loaded_line['DownVolume'])*.1:
                    action = "BUY"
                elif float(loaded_line['UpVolume'])+float(loaded_line['UpVolume'])*.1 < float(loaded_line['DownVolume']):
                    action = "SELLSHORT"
                else:
                    print("No Action Declared")
                    continue
                loaded_line['Close'] = float(loaded_line['Close'])
                if skip_line == 1:
                    prev_close = round(float(loaded_line['Close']), 2)
                    skip_line = 2
                    continue
                print("Actual Price: ", float(loaded_line['Close']))
                cur_close = round(float(loaded_line['Close']), 2)
            except Exception as e:
                print(e)
                continue
            if (prev_close < cur_close) and (cur_close <= (float(loaded_line['High'])) - .01) and (action == "BUY"):
                print('prev_close: ', prev_close, '\n', 'cur_close: ', cur_close)
                print('Buying Condition Triggered')
                return [prev_close,cur_close,action]
            if (prev_close > cur_close) and (cur_close >= (float(loaded_line['Low'])) - .01) and (action == "SELLSHORT"):
                print('prev_close: ', prev_close, '\n', 'cur_close: ', cur_close)
                print('Buying Condition Triggered')
                return [prev_close,cur_close,action]
            print('prev_close: ', prev_close, '\n', 'cur_close: ', cur_close)
            prev_close = cur_close
def cancel_order(buy_order_id):
    cancel_order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders/"
    order_view_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/"
    one_time_cancel = cancel_order_url + buy_order_id
    print(requests.request("DELETE", one_time_cancel, headers=headers()))
    while True:
        response = requests.request("GET", order_view_url + buy_order_id, headers=headers(),
                                    stream=True)
        if response.json()['Orders'][0]['StatusDescription'] == 'UROut':
            print('Order Cancelled')
            return True
        elif response.json()['Orders'][0]['StatusDescription'] == 'Filled':
            return False
        else:
            continue
def market_status():
    tz = pytz.timezone('UTC')
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=str(dt.date.today()), end_date=str(dt.date.today()))
    if schedule.empty:
        return False
    else:
        if (schedule['market_open'][0]) > datetime.now(pytz.utc):
            return False
        elif (schedule['market_close'][0] - timedelta(minutes=3)) < datetime.now(pytz.utc):
            return False
        else:
            return True
# def close_positions(tick):
#     cancel_order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders/"
#     position_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/positions"
#     order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders/"
#     print('Clossing Positions ...')
#     orders = pd.read_csv("orders.csv")
#     orders = orders[orders["Symbol"]==tick]
#     if len(orders) == 0:
#         return
#     for order in orders["Sell Order"]:
#         response = requests.request("DELETE", cancel_order_url + order, headers=headers())
#         print('Delete Order Sent Response: ', response.json())
#     time.sleep(3)
#     response = requests.request("GET", position_url, headers=headers())
#     quan = 0
#     for position in response.json()['Positions']:
#         if position['Symbol'] == tick:
#             quan = position['Quantity']
#         if quan != 0:
#             print("Quantity, ", quan)
#             payload = {
#                 "AccountID": "SIM1145924M",
#                 "Symbol": f"{tick}",
#                 "Quantity": str(quan),
#                 "OrderType": "Market",
#                 "TradeAction": "SELL",
#                 "Route": "Intelligent",
#                 "TimeInForce": {
#                     "Duration": "GTC"
#                 }
#             }
#             response = requests.request("POST", order_url, json=payload, headers=headers())
#             print('Close Order Sent Response: ', response.json()['Orders'][0]['Message'])
def algoTrader(tick,reward_to_risk):
    data = list()
    try:
        state = False
        while market_status():
            order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
            order_view_url = "https://sim-api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/"
            print(f"Watching {tick} Market . . .")
            price_list = buy_trigger(tick)
            difference = price_list[1] - price_list[0]
            print("difference: ",str(difference))
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": str(1),
                "OrderType": "Limit",
                "LimitPrice": str(round(price_list[0], 2)),
                "TradeAction": f"{price_list[2]}",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
            response = requests.request("POST", order_url, json=payload, headers=headers())
            print("Buy Order Sent Response: ", response.json()['Orders'][0]['Message'])
            buy_order_id = response.json()['Orders'][0]['OrderID']
            data.append(buy_order_id)
            response = requests.request("GET", order_view_url + buy_order_id, headers=headers(),
                                        stream=True)
            buy_order_time_limit = datetime.now()
            deleted = False
            state = True
            action = price_list[2]
            try:
                for line in response.iter_lines():
                    if line:
                        try:
                            line = json.loads(line)
                            limit_reached = (datetime.now() - buy_order_time_limit).total_seconds() > 30
                            if limit_reached:
                                deleted = cancel_order(buy_order_id)
                            if deleted:
                                break
                            if (line['StatusDescription'] == 'Filled') or limit_reached:
                                buy_price = float(line['Legs'][0]['ExecutionPrice'])
                                print("buy_price: ",buy_price)
                                print('Buy Order Filled @ ', buy_price)
                                if action == "BUY":
                                    limit_price = buy_price + difference
                                    action = "SELL"
                                    stop_loss = buy_price + (difference/reward_to_risk)
                                if action == "SELLSHORT":
                                    limit_price = buy_price - difference
                                    action = "BUYTOCOVER"
                                    stop_loss = buy_price - (difference / reward_to_risk)
                                limit_price = round(limit_price, 2)
                                print('Setting Sell Limit Order @ ', limit_price)
                                payload = {
                                    "Type":"BRK",
                                    "Orders":[
                                        {
                                            "AccountID": "SIM1145924M",
                                            "Symbol": tick,
                                            "Quantity": str(1),
                                            "OrderType": "Limit",
                                            "LimitPrice": str(limit_price),
                                            "TradeAction": f"{action}",
                                            "Route": "Intelligent",
                                            "TimeInForce": {
                                                "Duration": "GTC"
                                            }
                                        },
                                        {
                                            "AccountID": "SIM1145924M",
                                            "Symbol": tick,
                                            "Quantity": str(1),
                                            "OrderType": "StopMarket",
                                            "StopPrice": str(stop_loss),
                                            "TradeAction": f"{action}",
                                            "Route": "Intelligent",
                                            "TimeInForce": {
                                                "Duration": "GTC"
                                            }
                                        }
                                ]}
                                break
                        except Exception:
                            continue
                state = False
                if deleted:
                    continue
                response = requests.request("POST", order_url, json=payload, headers=headers())
                sell_order_id = response.json()['Orders'][0]['OrderID']
                data.append(sell_order_id)
                pd.DataFrame(data,columns=["id"]).to_csv("../orders.csv")
                print("Sell Order Sent Response: ", response.json()['Orders'][0]['Message'])
            except Exception as e:
                print("Error Occured: ",e)
                print('error')
                pass
    except KeyboardInterrupt:
        print('FailSafe Initiated')

    #     Will allow user to change stocks if neccesary

    if state:
        if not cancel_order(buy_order_id):
            buy_price = float(line['Legs'][0]['ExecutionPrice'])
            limit_price = buy_price + difference
            limit_price = round(limit_price, 2)
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": "MSFT",
                "Quantity": str(1),
                "OrderType": "Limit",
                "LimitPrice": str(limit_price),
                "TradeAction": f"{action}",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
            response = requests.request("POST", order_url, json=payload, headers=headers())
            print('Last Sell Order Sent Response: ', response.json()['Orders'][0]['Message'])
            sell_order_id = response.json()['Orders'][0]['OrderID']
    # close_positions(tick)

if __name__ == '__main__':
# dont for get to run key Updater before this
    while True:
        if market_status():
            algoTrader("MSFT",.01)