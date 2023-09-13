#  make sure stock is day trade able meaning low outstanding shares and below 100
# pre-market momentum just the first two bars
# 5min bars
# engulfing candles only (for right now)
# volume average from past day must be higher than 2mill
# takes profit from 50% off diff of last candle
# stop loss is set to the lowest low of the last two candles
import json
import multiprocessing
import subprocess
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from KeyUpdater import headers
import time


def execute_tick(sym):
    params = {
        'interval': '5',
        'unit': 'Minute',
    }
    url = f"https://api.tradestation.com/v3/marketdata/stream/barcharts/{sym}"
    response = requests.request("GET", url, params=params, headers=headers(), stream=True)
    final = dict()
    cur_time = ""
    init_round = True
    for line in response.iter_lines():
        if line:
            try:
                if init_round:
                    cur_time = json.loads(line)['TimeStamp']
                    init_round = False

                if cur_time != json.loads(line)['TimeStamp']:
                    break
                final = json.loads(line)
            except Exception as e:
                print(line)
                print(e)
                pass
    if float(final['Open']) < float(final['Close']):
        if str(round((float(final['Close']) - float(final['Open'])) * .5 + float(final['Close']),2)) == final['Close']:
            profit = str(float(final['Close'])+.01)
        else:
            profit = str(round((float(final['Close']) - float(final['Open'])) * .5 + float(final['Close']),2))
        payload = {
            "AccountID": "SIM1145924M",
            "Symbol": f"{sym}",
            "Quantity": "1",
            "OrderType": "Limit",
            "LimitPrice": final['Close'],
            "TradeAction": "BUY",
            "TimeInForce": {
                "Duration": "GTC"
            },
            "Route": "Intelligent",
            "OSOs": [
                {
                    "Type": "BRK",
                    "Orders": [
                        {
                            "AccountID": "SIM1145924M",
                            "Symbol": f"{sym}",
                            "Quantity": "1",
                            "OrderType": "Limit",
                            "LimitPrice": profit,
                            "TradeAction": "SELL",
                            "TimeInForce": {
                                "Duration": "GTC"
                            },
                            "Route": "Intelligent"
                        },
                        {
                            "AccountID": "SIM1145924M",
                            "Symbol": f"{sym}",
                            "Quantity": "1",
                            "OrderType": "StopMarket",
                            "TradeAction": "SELL",
                            "StopPrice": final['Low'],
                            "TimeInForce": {
                                "Duration": "GTC"
                            },
                            "Route": "Intelligent"
                        }
                    ]
                }
            ]
        }
        url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
        response = requests.request("POST", url, json=payload, headers=headers())
        print(response.json())
    print('Finished Running: ',sym)

def flag_tick(sym):
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/{sym}"
    params = {
        'interval': '5',
        'unit': 'Minute',
        'barsback': '2'
    }
    response = requests.request("GET", url, params=params, headers=headers())
    last_bar = response.json()['Bars'][0]
    cur_bar = response.json()['Bars'][1]
    if float(last_bar['Low']) > float(cur_bar['Low']):
        return sym
    return


def process_tick(sym):
    try:
        info_sym = yf.Ticker(sym)
        try:
            if info_sym.info['volume'] < 10000000:
                return

        except Exception:
            try:
                if info_sym.info['regularMarketVolume'] < 10000000:
                    return
            except Exception:
                return

        if info_sym.info["currentPrice"] >= 200 :
            return
        if info_sym.info["currentPrice"] <= 1:
            return
        graph_data = yf.download(sym, start=datetime.now() - timedelta(days=3), prepost=True, interval='1m',
                                 progress=False)
        if graph_data.empty:
            return
        return sym
    except Exception:
        return


if __name__ == '__main__':
    # Step 1: Look for stocks that meet the requisites
    while True:
        command = "pip install yfinance --upgrade"
        try:
            subprocess.check_output(command, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        watchlist = pd.read_csv("../watchlist.csv")
        if str(datetime.now().date()) != watchlist.columns[0]:
            nasdaq = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
            nyse = requests.get("http://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt")
            file = open("../ticker_list.txt", "w")
            file.write(str(nasdaq.text))
            file.write(str(nyse.text))
            file.close()
            ticker_list = pd.read_csv("../ticker_list.txt", sep="|")
            result = list()
            num_cores = multiprocessing.cpu_count()
            try:
                with multiprocessing.Pool(processes=num_cores) as pool:
                    # Use pool.map to apply the method to each chunk in parallel
                    result = pool.map(process_tick, list(ticker_list["Symbol"]))
            except Exception:
                pass
            watchlist = [item for item in result if item is not None]
            # Step 2: Figure out a way to track volume increase based off different parts of the day (wait for market to be open again
            # Step 3: Check if last candle is bull or bear candle
            pd.Series(watchlist,name=datetime.now().date()).to_csv('../watchlist.csv', index = False)
        else:
            watchlist = list(watchlist[watchlist.columns[0]])
        flagged_stocks = list()
        try:
            num_cores = multiprocessing.cpu_count()
            with multiprocessing.Pool(processes=num_cores) as pool:
                # Use pool.map to apply the method to each chunk in parallel
                flagged_stocks = pool.map(flag_tick, watchlist)
        except Exception:
            pass
        flagged_stocks = [item for item in flagged_stocks if item is not None]
        try:
            flagged_stocks = flagged_stocks[:num_cores]
        except Exception:
            pass
        print(flagged_stocks)
        with multiprocessing.Pool(processes=num_cores) as pool:
            pool.map(execute_tick, flagged_stocks)

    # New Concept Buy New Low and Bull/Undeciding Candle
    # Stoploss is set the low
    # Step 4 - Bull Candle: Open Current Candle is less than Open Last Candle
    # Step 4 - Bear Candle: Open Current Candle is less than Close Last Candle
    # Step 5: Flag that stock down
    # Step 6: Watch Stock till finish
    # Step 6.5 - Bull Candle:  Close Current Candle is greater than Close Last Candle
    # Step 6.5 - Bear Candle:  Close Current Candle is greater than Open Last Candle
    # If condition is met continue to Step 7 else Step 1
    # Step 7:
    # - Limit Buy at Close Current Candle
    # - Loss  StopLoss Sell at the lesser between Low Current Candle and Low Last Candle
    # - Profit StopPrice Sell at Close Current Candle+(50% of Close Current Candle - Open Current Candle)
    # Execute OSO then return to Step 1
