import time

import pandas as pd
import requests
import multiprocessing
from KeyUpdater import headers, get_access_token
from datetime import datetime, timedelta

def get_symbol():
    while True:
        try:
            symbol = input("Enter Company's ticker Symbol:")
            # Check if symbol exists
            url = f"https://api.tradestation.com/v3/marketdata/quotes/{symbol}"
            response = requests.request("GET", url, headers=headers())
            ticker = response.json()['Quotes'][0]['Symbol']
            return ticker
        except Exception as e:
            print(e)
            print('Not an existing symbol. Please try again')
            continue
def get_data(tick):
    while True:
        try:
            url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}"
            interval = input("Enter interval:")
            firstdate = input("Start Date(EX: YYYY-MM-DD):")
            lastdate = input("End Date(EX: YYYY-MM-DD):")
            if firstdate == "":
                firstdate = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z')
                lastdate = datetime.now().strftime('%Y-%m-%dT00:00:00Z')
            else:
                firstdate = datetime.strptime(firstdate,'%Y-%m-%d').strftime('%Y-%m-%dT00:00:00Z')
                lastdate = datetime.strptime(lastdate,'%Y-%m-%d').strftime('%Y-%m-%dT00:00:00Z')
            params ={
                'unit':'Minute',
                "interval": str(interval),
                'firstdate':firstdate,
                'lastdate': lastdate
            }
            response = requests.request("GET", url,params=params, headers=headers())
            # print(response.text)
            bars = response.json()['Bars']
            return bars
        except Exception as e:
            print(e)
            print('Error occured')
            continue
def process_data(data):
    df = pd.DataFrame()
    for bar in data:
        new_index = len(df)
        df.loc[new_index,'High'] = float(bar['High'])
        df.loc[new_index, 'Low'] = float(bar['Low'])
        df.loc[new_index, 'Close'] = float(bar['Close'])
        df.loc[new_index, 'Open'] = float(bar['Open'])
        df.loc[new_index, 'TimeStamp'] = datetime.strptime(bar['TimeStamp'],"%Y-%m-%dT%H:%M:%SZ")
        df.loc[new_index, 'TotalVolume'] = float(bar['TotalVolume'])
        df.loc[new_index, 'DownTicks'] = bar['DownTicks']
        df.loc[new_index, 'DownVolume'] = bar['DownVolume']
        df.loc[new_index, 'TotalTicks'] = bar['TotalTicks']
        df.loc[new_index, 'UpTicks'] = bar['UpTicks']
        df.loc[new_index, 'UpVolume'] = bar['UpVolume']
    return df
def select_algorithm():
    while True:
        try:
            print("Enter File(without extension")
            print("File must be within Folder")
            module = input("File:")
            imported_module = __import__(module)
            print(dir(imported_module))
            function = input("Enter Function:")
            function = getattr(imported_module,function)
            break
        except Exception as e:
            print(e)
            continue
    return function
if __name__ == '__main__':
    token_run = multiprocessing.Process(target=get_access_token)
    token_run.start()
    time.sleep(5)
    print("Welcome to Algo Back Tester")
    tick = get_symbol()
    data = get_data(tick)
    df = process_data(data)
    strategy = select_algorithm()
    result_df = strategy(df)
    token_run.terminate()