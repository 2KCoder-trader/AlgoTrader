import pandas as pd
import numpy as np
import math
from KeyUpdater import headers
from datetime import datetime, timedelta
import requests
import time
import yfinance as yf
import json
import multiprocessing


# New Strategy


# 1. On new High Candle you buy on the next Candle Open
# 2. Set Stop Loss at Low of Candle with New High Indicater
# Either set Profit Stop  at 1:1 of Stop Loss Reward:Risk Ratio should be 1:1
# Stops Trading around 1

def load_data():
    num_cores = multiprocessing.cpu_count()
    p = list()
    try:
        with multiprocessing.Pool(processes=num_cores) as pool:
            # Use pool.map to apply the method to each chunk in parallel
            p = pool.map(run_day, [x for x in range(1,30)])
    except Exception as e:
        pass
    print(p)
    print("SUM: ",sum(p))




def run_day(day):
    today = datetime.now()
    data_url = "https://api.tradestation.com/v3/marketdata/barcharts/AAPL"
    params = {
        "interval": 1,
        "unit": "Minute",
        "firstdate": (datetime(today.year, month=today.month, day=today.day, hour=9, minute=30) - timedelta(
            days=day)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lastdate": (datetime(year=today.year, month=today.month, day=today.day, hour=12) - timedelta(
            days=(day - 1))).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    response = requests.request("GET", data_url, params=params, headers=headers())
    prev_high = np.nan
    stop_loss = np.nan
    profit_stop = np.nan
    buy_in = 0
    bar = np.nan
    profit = 0
    try:
        if response.json():
            for bar in response.json()['Bars']:
                if buy_in == 1:
                    buy_in = 2
                    buy_at = float(bar["Open"])
                    profit_stop = buy_at + (buy_at - stop_loss)

                if buy_in == 2:
                    if float(bar["High"]) >= profit_stop * 1:
                        profit += (profit_stop * 1) - buy_at
                        buy_in = 0
                    elif float(bar["Low"]) <= stop_loss:
                        profit += stop_loss - buy_at
                        buy_in = 0


                elif buy_in == 0:
                    if prev_high != np.nan:
                        if (prev_high < float(bar['High'])) and (abs(float(bar['Close']) - float(bar['Open'])) > .01):
                            stop_loss = float(bar["Low"])
                            buy_in = 1
                prev_high = float(bar['High'])
            if buy_in == 2:
                profit += float(bar['Close']) - buy_at
            print(profit)
            return profit
    except KeyError:
        return 0


if __name__ == '__main__':
    load_data()