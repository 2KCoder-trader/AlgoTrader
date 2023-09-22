import keyboard
import pandas as pd
import re

import yf as yf

from Algo_BackTest import process_data
import pandas_market_calendars as mcal
import requests
from KeyUpdater import headers, get_access_token
from datetime import datetime, timedelta
import datetime as dt
import pytz

import json


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


def calculate_profitloss(group_list,consec,change):
    tot_pl = 0
    wins = 0
    tots = 0
    if len(group_list) != 0:
        url = f"https://sim-api.tradestation.com/v3/brokerage/accounts/SIM1145924M/orders/{','.join(group_list)}"
        response = requests.request("GET", url, headers=headers())
        for i in range(0, len(group_list), 3):

            order_pl = 0
            order_detail_entry = response.json()['Orders'][i]
            order_detail_profit = response.json()['Orders'][i + 1]
            order_detail_stop = response.json()['Orders'][i + 2]
            quantity = float(order_detail_entry['Legs'][0]['ExecQuantity'])
            exec_price = float(order_detail_entry['Legs'][0]['ExecutionPrice'])
            if order_detail_entry['Status'] != 'FLL':
                continue
            elif order_detail_profit['Status'] == 'FLL':
                order_pl += float(order_detail_profit['Legs'][0]['ExecutionPrice']) - exec_price
                wins += 1
            elif order_detail_stop['Status'] == 'FLL':
                order_pl += float(order_detail_stop['Legs'][0]['ExecutionPrice']) - exec_price
            order_pl *= quantity
            tot_pl += order_pl
            change.append(order_pl)
            consec.append(tot_pl)
            return [tot_pl, tots, wins,consec,change]
    else:
        return


if __name__ == '__main__':
    orders = pd.DataFrame(columns=['Entry', 'Profit', 'StopLoss'])
    file = __import__(input('File Name: '))
    print(dir(file))
    function = input("Select Function (to set preferences):")
    preferences = getattr(file, function)()
    function = input("Select Function (to test):")
    algorithm = getattr(file, function)
    tot_pl = 0
    tot_ord = 0
    tot_wins = 0
    consec = list()
    change = list()
    group_list = list()
    groups = 0
    if preferences['unit'] == 'urownthing':
        while market_status():
            ids = algorithm()
            if ids:
                groups += 1
                group_list.append(str(ids['Entry']))
                group_list.append(str(ids['Profit']))
                group_list.append(str(ids['StopLoss']))
            if groups == 15:
                info = calculate_profitloss(group_list)
                tot_pl += info[0]
                tot_ord += info[1]
                tot_wins += info[2]
                consec = info[3]
                change += info[4]
                groups = 0
                group_list = list()
            if keyboard.is_pressed('esc'):
                break

    elif preferences['unit'] == 'fastasfuckboii':
        url = f"https://api.tradestation.com/v2/stream/tickbars/{preferences['symbol']}/1/1"
        data = list()
        while market_status():
            response = requests.request("GET", url, headers=headers(), stream=True)
            bars = 0
            for line in response.iter_lines():
                if line:
                    line = json.loads(line)
                    if preferences['barsback'] == bars:
                        break
                    data.append(line['Close'])
                    bars += 1
            ids = algorithm(data)
            if ids:
                groups += 1
                group_list.append(str(ids['Entry']))
                group_list.append(str(ids['Profit']))
                group_list.append(str(ids['StopLoss']))
            if groups == 15:
                info = calculate_profitloss(group_list)
                tot_pl += info[0]
                tot_ord += info[1]
                tot_wins += info[2]
                consec = info[3]
                change += info[4]
                groups = 0
                group_list = list()
            if keyboard.is_pressed('esc'):
                break
    elif preferences['unit'] == 'Seconds':
        url = f"https://api.tradestation.com/v2/stream/tickbars/{preferences['symbol']}/1/{preferences['barsback']}"
        while True:
            response = requests.request("GET", url, headers=headers(), stream=True)
            cur_date = datetime.now()
            # collect data
            bars = 0
            interval = 1
            data = list()
            for line in response.iter_lines():
                if line:
                    line = json.loads(line)
                    numbers = re.findall(r'\d+', line['TimeStamp'])
                    timestamp = int(numbers[0]) / 1000
                    date = datetime.fromtimestamp(timestamp)
                    if cur_date == date:
                        continue
                    if preferences['interval'] < interval:
                        interval += 1
                        continue
                    else:
                        interval = 1
                    data.append(line['Close'])
                    cur_date = date
                    if preferences['barsback'] == bars:
                        break
                    bars += 1
            ids = algorithm(data)
            if ids:
                groups += 1
                group_list.append(str(ids['Entry']))
                group_list.append(str(ids['Profit']))
                group_list.append(str(ids['StopLoss']))
            if groups == 15:
                info = calculate_profitloss(group_list)
                tot_pl += info[0]
                tot_ord += info[1]
                tot_wins += info[2]
                consec = info[3]
                change += info[4]
                groups = 0
                group_list = list()
            if keyboard.is_pressed('esc'):
                break
    else:
        params = {
            'unit': preferences['unit'],
            "interval": str(preferences['interval']),
            'barsback': str(preferences['barsback'])
        }
        url = f"https://api.tradestation.com/v3/marketdata/barcharts/{preferences['symbol']}"
        while True:
            response = requests.request("GET", url, params=params, headers=headers())
            bars_df = process_data(response.json()['Bars'])
            ids = algorithm(bars_df)
            if ids:
                groups += 1
                group_list.append(str(ids['Entry']))
                group_list.append(str(ids['Profit']))
                group_list.append(str(ids['StopLoss']))
            if groups == 15:
                info = calculate_profitloss(group_list)
                tot_pl += info[0]
                tot_ord += info[1]
                tot_wins += info[2]
                consec = info[3]
                change += info[4]
                groups = 0
                group_list = list()
            if keyboard.is_pressed('esc'):
                break
    info = calculate_profitloss(group_list)
    tot_pl += info[0]
    tot_ord += info[1]
    tot_wins += info[2]
    consec = info[3]
    change += info[4]
    print('Profit\\Loss: ',str(tot_pl))
    print('Win Rate: ',str(tot_wins/tot_ord))
    print(consec)
    print(change)