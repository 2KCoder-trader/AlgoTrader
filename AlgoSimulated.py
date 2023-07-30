import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
from IPython.display import clear_output
import requests
import json
import time
import pytz
import pandas_market_calendars as mcal
import datetime as dt
import math
from KeyUpdater import headers
from AccountsSim import get_balance


def ordering():
    trade_balance = pd.read_csv("trade_balance.csv")
    trade_bal = trade_balance[0][0]
    trade_balance.iloc[0, 0] = 0
    trade_balance.to_csv("trade_balance.csv")
#     ---------------------------------------
#     trade_bal would be subtracted here
#     done ordering
    trade_balance = pd.read_csv("trade_balance.csv")
    trade_balance.iloc[0, 0] = trade_bal
    trade_balance.to_csv("trade_balance.csv")




def stock_check(tick):
    stock_info = yf.Ticker(tick).info
    if stock_info['previousClose'] > 5:
        return " "
    while True:
        if stock_info['previousClose'] < 1:
            stock_info['previousClose'] = stock_info['previousClose']*10
            continue
        if stock_info['previousClose'] > 5:
            return " "
        else:
            break
    print('recommendationKey: ', stock_info['recommendationKey'])
    if ('hold' == stock_info['recommendationKey']) or ('none' == stock_info['recommendationKey']) or (
            'underperform' == stock_info['recommendationKey']) or (
            'sell' == stock_info['recommendationKey']):
        return " "
    return tick

def close_positions(tick):
    print('Clossing Positions ...')
    orders = pd.read_csv("orders.csv")
    orders = orders[orders["Symbol"]==tick]
    if len(orders) == 0:
        return
    for order in orders["Sell Order"]:
        response = requests.request("DELETE", cancel_order_url + order, headers=headers())
        print('Delete Order Sent Response: ', response.json())
    time.sleep(3)
    response = requests.request("GET", position_url, headers=headers())
    quan = 0
    for position in response.json()['Positions']:
        if position['Symbol'] == tick:
            quan = position['Quantity']
        if quan != 0:
            print("quan, ", quan)
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": f"{tick}",
                "Quantity": str(quan),
                "OrderType": "Market",
                "TradeAction": "SELL",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
            response = requests.request("POST", order_url, json=payload, headers=headers())
            print('Close Order Sent Response: ', response.json()['Orders'][0]['Message'])


# def annual_rate_of_return(trade_count, buy_price):
#     #     unsettled = balance['UnsettledFunds']
#     reprofit = balance['RealizedProfitLoss'] + balance['RealizedProfitLoss'] UnrealizedProfitLoss
#     unsettled = trade_count * buy_price
#     print("Cost: ", unsettled)
#     initial = unsettled * 3
#     final = initial
#     day_return = reprofit / initial
#     for x in range(84):
#         final = final * (day_return + 1)
#     gain = final - initial
#     return str((gain / 10000) * 100) + '%'


def volume(tick):
    print("Running Volume")
    params = {
        "interval": "1",
        "unit": "minute",
        "barsback": "3"
    }
    response = requests.request("GET", f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}",
                                params=params, headers=headers())
    print(response)
    print(json.dumps(response.json(), indent=4))
    volume0 = float(response.json()['Bars'][0]['TotalVolume'])
    volume1 = float(response.json()['Bars'][1]['TotalVolume'])
    volume2 = float(response.json()['Bars'][2]['TotalVolume'])
    print("5Min Volume: ", volume0, " ", volume1, " ", volume2)
    if (volume0 < 10000) & (volume1 < 10000) & (volume2 < 10000):
        print("Sleeping")
        return 0
    if (volume0 <= 1600000) & (volume1 <= 1600000) & (volume2 <= 1600000):
        return 3
    else:
        return 2


def market_status():
    tz = pytz.timezone('UTC')
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=str(dt.date.today()), end_date=str(dt.date.today()))
    if schedule.empty:
        return [False]
    else:
        if (schedule['market_open'][0] + timedelta(minutes=25)) > datetime.now(pytz.utc):
            return [False]
        elif (schedule['market_close'][0] - timedelta(minutes=3)) < datetime.now(pytz.utc):
            return [False]
        else:
            return [True, 1 - (schedule['market_close'][0] - datetime.now(tz=tz)).total_seconds() / (
                    schedule['market_close'][0] - schedule['market_open'][0]).total_seconds()]


def share_amount(balance,prev_close):
    trade_bal = pd.read_csv("trade_balance.csv")
    day_percentage = market_status()[1]
    print("day_percentage: ", day_percentage)
    print("trade_bal: ", trade_bal)
    print("balance/3: ", balance)
    next_trade_cost = ((balance) * day_percentage) - ((balance) - trade_bal)
    print("next_trade_cost: ", next_trade_cost)
    if next_trade_cost > prev_close:
        if math.floor(next_trade_cost / prev_close) > 10:
            return 10
        else:
            return math.floor(next_trade_cost / prev_close) > 10
    else:
        return 0


order_view_url = "https://sim-api.tradestation.com/v3/brokerage/stream/accounts/SIM1145924M/orders/"
nostream_order_view_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/"
all_order_view_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders"
order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
cancel_order_url = "https://sim-api.tradestation.com/v3/orderexecution/orders/"
position_url = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/positions"
balances = "https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/balances"

def algoTrader(tick):
    global buy_order_id, line
    stream_url = f"https://api.tradestation.com/v3/marketdata/stream/barcharts/{tick}"
    trade_count = 0
    order_count = 0
    skip_line = 0
    state = False
    cur_close = 0
    prev_close = 0
    difference = 0
    deleted = False
    next_share_amount = 0
    balance = get_balance()
    print("Algorithm Starting")
    while True:
        multiplier = 1
        try:
            print("Checking Market Status")
            if market_status()[0] == False:
                print("Market Closed")
                time.sleep(300)
                continue
            print("Market Open")
            if stock_check(tick) == " ":
                close_positions(tick)
                return " "

#               put account calulations and returning here this is the difference between simulated and live




            # end
            print('Number of Trades: ', trade_count)
            level = volume(tick)
            if level == 0:
                time.sleep(30)
                continue
            print("Getting level: ", level)
            print(f"Watching {tick} Market . . .")
            response = requests.request("GET", stream_url, headers=headers(), stream=True)
            wait_time = datetime.now()+timedelta(hours = 1)
            for line in response.iter_lines():
                if line:
                    if skip_line == 0:
                        skip_line = 1
                        continue
                    line = json.loads(line)
                    try:
                        line['Close'] = float(line['Close'])
                        while True:
                            if line['Close']<1:
                                multiplier *= 10
                                line['Close'] = line['Close']*10
                                continue
                            else:
                                break
                        if skip_line == 1:
                            prev_close = cur_close = round(float(line['Close']), 2)
                            skip_line = 2
                            continue
                        print("Actual Price: ", float(line['Close']))
                        price_shape = float(line['Close'])
                        if level == 3:
                            cur_close = round(price_shape, 2)
                        elif level == 2:
                            cur_close = round(price_shape, 1)
                    except Exception as e:
                        print(e)
                        continue
                    if (prev_close < cur_close) and (cur_close <= (float(line['High'])*multiplier) - .01):
                        print('prev_close: ', prev_close, '\n', 'cur_close: ', cur_close)
                        print('Buying Condition Triggered')
                        break
                    print('prev_close: ', prev_close, '\n', 'cur_close: ', cur_close)
                    prev_close = cur_close
                    if datetime.now()> wait_time:
                        return
            skip_line = 0
            difference = cur_close - prev_close
            difference /= multiplier
            next_share_amount = share_amount(balance, prev_close)
            temp_trade_bal = pd.read_csv("trade_balance.csv")[0][0]
            pd.DataFrame([0]).to_csv("trade_balance.csv")
            if next_share_amount == 0:
                continue
            #     replace with prev_close
            if level == 2:
                print("Initiating Level 2 Order")
                payload = {
                    "AccountID": "SIM1145924M",
                    "Symbol": tick,
                    "Quantity": str(next_share_amount*multiplier),
                    "OrderType": "StopMarket",
                    "TradeAction": "BUY",
                    "AdvancedOptions": {
                        "TrailingStop": {
                            "Percent": "5.0"
                        }
                    },
                    "Route": "Intelligent",
                    "TimeInForce": {
                        "Duration": "GTC"
                    }
                }
                response = requests.request("POST", order_url, json=payload, headers=headers())
                try:
                    prev_close = 0
                    cur_close = 0
                    print("Buy Order Sent Response: ", response.json()['Orders'][0]['Message'])
                    continue
                except Exception:
                    print("Order Not Executed")
                    continue
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": tick,
                "Quantity": str(next_share_amount),
                "OrderType": "Limit",
                "LimitPrice": str(round(prev_close, 2)),
                "TradeAction": "BUY",
                "Route": "Intelligent",
                "TimeInForce": {
                    "Duration": "GTC"
                }
            }
            print("Initiating Level 3 Order")
            response = requests.request("POST", order_url, json=payload, headers=headers())
            prev_close = 0
            cur_close = 0
            print("Buy Order Sent Response: ", response.json()['Orders'][0]['Message'])
            buy_order_id = response.json()['Orders'][0]['OrderID']
            response = requests.request("GET", order_view_url + buy_order_id, headers=headers(),
                                        stream=True)
            buy_order_time_limit = datetime.now()
            print("Buy Order Filled: ")
            try:
                for line in response.iter_lines():
                    if line:
                        try:
                            line = json.loads(line)
                            print("False", end="\r")
                            limit_reached = (datetime.now() - buy_order_time_limit).total_seconds() > 30
                            if (limit_reached):
                                one_time_cancel = cancel_order_url + buy_order_id
                                response = requests.request("DELETE", one_time_cancel, headers=headers())
                                response = requests.request("GET", nostream_order_view_url + buy_order_id, headers=headers(),
                                                            stream=True)
                                print('response: ', response.json())
                                if response.json()['Orders'][0]['StatusDescription'] == 'UROut':
                                    print('Order Cancelled')
                                    state = False
                                    deleted = True
                                    break
                                elif response.json()['Orders'][0]['StatusDescription'] == 'Filled':
                                    line = response.json()['Orders'][0]
                                    deleted = False
                                else:
                                    continue
                            if deleted == True:
                                break
                            if (line['StatusDescription'] == 'Filled'):
                                print("\r", end="")
                                print("True", end="")
                                buy_price = float(line['Legs'][0]['ExecutionPrice'])

                                temp_trade_bal -= buy_price * next_share_amount
                                pd.DataFrame([temp_trade_bal]).to_csv("trade_balance.csv")
                                print('Buy Order Filled @ ', buy_price)
                                limit_price = buy_price + difference
                                limit_price = round(limit_price, 2)
                                print('Setting Sell Linit Order @ ', limit_price)
                                payload = {
                                    "AccountID": "SIM1145924M",
                                    "Symbol": tick,
                                    "Quantity": str(next_share_amount),
                                    "OrderType": "Limit",
                                    "LimitPrice": str(limit_price),
                                    "TradeAction": "SELL",
                                    "Route": "Intelligent",
                                    "TimeInForce": {
                                        "Duration": "GTC"
                                    }
                                }
                                break

                        except Exception:
                            continue
                if deleted:
                    deleted = False
                    continue
                response = requests.request("POST", order_url, json=payload, headers=headers())
                trade_count += next_share_amount
                print("Sell Order Sent Response: ", response.json()['Orders'][0]['Message'])
                sell_order_id = response.json()['Orders'][0]['OrderID']
                orders = pd.read_csv("orders.csv")
                index = len(orders)
                orders.loc[index,"Symbol"] = tick
                orders.loc[index, "Sell Order"] = sell_order_id
                orders.to_csv("orders.csv")
                state = False
                response = requests.request("GET", balances, headers=headers())
                print("Running Stats:", json.dumps(response.json(), indent=4))
            except Exception as e:
                print(e)
                print('error')
                pass
        except KeyboardInterrupt:
            print('FailSafe Initiated')

            #     Will allow user to change stocks if neccesary

            if state:
                one_time_cancel = cancel_order_url + buy_order_id
                response = requests.request("DELETE", one_time_cancel, headers=headers())
                time.sleep(10)
                response = requests.request("GET", nostream_order_view_url + buy_order_id, headers=headers())
                if response.json()['Orders'][0]['StatusDescription'] == 'Filled':
                    buy_price = float(line['Legs'][0]['ExecutionPrice'])
                    limit_price = buy_price + difference
                    limit_price = round(limit_price, 2)
                    payload = {
                        "AccountID": "SIM1145924M",
                        "Symbol": "MSFT",
                        "Quantity": str(next_share_amount),
                        "OrderType": "Limit",
                        "LimitPrice": str(limit_price),
                        "TradeAction": "SELL",
                        "Route": "Intelligent",
                        "TimeInForce": {
                            "Duration": "GTC"
                        }
                    }
                    response = requests.request("POST", order_url, json=payload, headers=headers())
                    trade_count += next_share_amount
                    order_count += 1
                    print('Last Sell Order Sent Response: ', response.json()['Orders'][0]['Message'])
                    sell_order_id = response.json()['Orders'][0]['OrderID']
                    orders = pd.read_csv("orders.csv")
                    index = len(orders)
                    orders.loc[index, "Symbol"] = tick
                    orders.loc[index, "Sell Order"] = sell_order_id
                    orders.to_csv("orders.csv")
            close_positions(tick)
            break
