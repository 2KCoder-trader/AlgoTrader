import time

import pandas as pd
import pandas_market_calendars as mcal
import requests
from sklearn.ensemble import RandomForestRegressor

from KeyUpdater import headers, get_access_token
from datetime import datetime, timedelta
import datetime as dt
import pytz
import multiprocessing

import json
def market_status():
    tz = pytz.timezone('UTC')
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=str(dt.date.today()), end_date=str(dt.date.today()))
    if schedule.empty:
        return [False]
    else:
        if (schedule['market_open'][0] + timedelta(minutes=25)) > datetime.now(pytz.utc):
            return False
        elif (schedule['market_close'][0] - timedelta(minutes=3)) < datetime.now(pytz.utc):
            return False
        else:
            return True
if __name__ == '__main__':

    # use last weekday data to train model
    tick = 'TSLA'
    multiprocessing.freeze_support()
    multiprocessing.Process(target=get_access_token).start()
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}"
    firstdate = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z')
    lastdate = datetime.now().strftime('%Y-%m-%dT00:00:00Z')
    params = {
        'interval': 1,
        'unit': 'Minute',
        'firstdate':firstdate,
        'lastdate':lastdate
    }
    response = requests.request("GET", url, headers=headers(), params=params)
    bars = response.json()['Bars']
    from Algo_BackTest import process_data
    data = process_data(bars)
    data['Date'] = data['TimeStamp'].apply(lambda x: x.date())
    lastest_date = ''
    for date in data['Date'].unique():
        if len(data[data['Date']==date]) >= 390:
            lastest_date = date
    test_data = data[data['Date']==date]
    data['Future Close'] = data['Close'].shift(-1)
    data.drop(len(data) - 1, inplace=True)
    data = data.reset_index()
    X_data = data.drop(['Future Close', 'TimeStamp','Date'], axis=1)
    y_data = data['Future Close']
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_data, y_data)
    last_now = datetime.now()
    orders = pd.DataFrame(columns=['Entry','Profit','StopLoss'])
    while True:
        if datetime.now() > datetime(year=last_now.year,month=last_now.month,day=last_now.day,hour=last_now.hour,
                                     minute=(last_now+timedelta(minutes=1)).minute,second=1):
            print("Starting New Order")
            # This is initial phase because we actually trying to compare between predicting values
            url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}"
            params = {
                'interval': 1,
                'unit': 'Minute',
                'barsback':3
            }
            response = requests.request("GET", url, headers=headers(), params=params)
            print("response: ", response)
            bars = response.json()['Bars']
            bars = process_data(bars)
            X_test = bars.drop(['TimeStamp'], axis=1)
            X_test = X_test.reset_index()
            pred_y = regressor.predict(X_test)
            action = ''
            if pred_y[0] <= pred_y[1]:
                print("Short Order")
                buy_action = 'SELLSHORT'
                sell_action = 'BUYTOCOVER'
            else:
                print('Long Order')
                buy_action = 'BUY'
                sell_action = 'SELL'

            url = "https://sim-api.tradestation.com/v3/orderexecution/orders"

            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": f"{tick}",
                "Quantity": "10",
                "OrderType": "Market",
                "TradeAction": f"{buy_action}",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent"
            }
            buy_response = requests.request("POST", url, json=payload, headers=headers())
            print(response.json())

            time.sleep(60)
            payload = {
                "AccountID": "SIM1145924M",
                "Symbol": f"{tick}",
                "Quantity": "10",
                "OrderType": "Market",
                "TradeAction": f"{sell_action}",
                "TimeInForce": {"Duration": "DAY"},
                "Route": "Intelligent"
            }
            sell_response = requests.request("POST", url, json=payload, headers=headers())
            print(response.json())
            last_now = datetime.now()
            # market sell


