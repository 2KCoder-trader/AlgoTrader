import yfinance as yf
import json
import AccountsSim
import multiprocessing
import AlgoSimulated
import pandas as pd
from Idle import Idle
from KeyUpdater import get_access_token
import requests
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
def stock_picker(ticks):
    for tick in ticks:
        try:
            stock_info = yf.Ticker(tick).info
            if stock_info['previousClose'] > 4.5:
                continue
            if stock_info['previousClose'] < 1.5:
                continue
            if ('hold' == stock_info['recommendationKey']) or ('none' == stock_info['recommendationKey']) or (
                    'underperform' == stock_info['recommendationKey']) or (
                    'sell' == stock_info['recommendationKey'])or (
                    'buy' == stock_info['recommendationKey']):
                continue
            if stock_info['volume'] < 10000000:
                continue
            multiprocessing.Process(target=AlgoSimulated.algoTrader, args=[tick]).start()
            print("Processors: ",multiprocessing.active_children())
            while len(multiprocessing.active_children()) >= 9:
                print("Processors at capacity",end = "\r")
        except Exception as e:
            print("Error occured: ",e)


if __name__ == '__main__':
    multiprocessing.Process(target=AccountsSim.AccountsSim).start()
    multiprocessing.Process(target=Idle).start()
    multiprocessing.Process(target=get_access_token).start()
    # Put the function below in accountsim
    while True:
        page_to_scrape = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
        file = open("nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", "w")
        file.write(str(page_to_scrape.text))
        file.close()
        nasdaq = pd.read_csv("nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", sep="|")
        nasdaq.drop(len(nasdaq) - 1, axis=0, inplace=True)
        stock_picker(nasdaq['Symbol'])
