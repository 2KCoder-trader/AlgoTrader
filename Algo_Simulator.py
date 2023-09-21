import pandas as pd
import re
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
        if (schedule['market_open'][0] + timedelta(minutes=5)) > datetime.now(pytz.utc):
            return False
        elif (schedule['market_close'][0] - timedelta(minutes=3)) < datetime.now(pytz.utc):
            return False
        else:
            return True
if __name__ == '__main__':
    print("What do you want this run to be called?")
    order_name = input()
    orders = pd.DataFrame()
    file = __import__(input('File Name: '))
    print(dir(file))
    function = input("Select Function (to set preferences):")
    preferences = getattr(file, function)()
    function = input("Select Function (to test):")
    algorithm = getattr(file, function)
    while market_status():
    # while True:
        if preferences['unit'] == 'fastasfuckboii':
            url = f"https://api.tradestation.com/v2/stream/tickbars/{preferences['symbol']}/1/1"
            data = list()
            while True:
                response = requests.request("GET", url, headers=headers(), stream=True)
                bars = 0
                for line in response.iter_lines():
                    if line:
                        if preferences['barsback'] == bars:
                            break
                        data.append(line['Close'])
                        bars += 1
                ids = algorithm(bars)
                orders = pd.concat([orders, pd.Series(ids)]).reset_index(drop=True)
                orders.to_csv(f'{order_name}.csv')
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
                orders = pd.concat([orders, pd.Series(ids)]).reset_index(drop=True)
                orders.to_csv(f'{order_name}.csv')
        else:
            params = {
                    'unit':preferences['unit'],
                    "interval": str(preferences['interval']),
                    'barsback': str(preferences['barsback'])
                }
            url = f"https://api.tradestation.com/v3/marketdata/barcharts/{preferences['symbol']}"
            while True:
                response = requests.request("GET", url, params=params, headers=headers())
                bars_df = process_data(response.json()['Bars'])
                ids = algorithm(bars_df)
                orders = pd.concat([orders,pd.Series(ids)]).reset_index(drop= True)
                orders.to_csv(f'{order_name}.csv')


















