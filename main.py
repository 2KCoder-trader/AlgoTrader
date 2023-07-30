import yfinance as yf
import json
import AccountsSim
import multiprocessing
import AlgoSimulated
import subprocess
import pandas as pd
from Idle import Idle
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
                    'sell' == stock_info['recommendationKey']):
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
    multiprocessing.Process(target=AccountsSim.AccountsSim).start()
    command = "pip install yfinance --upgrade"
    try:
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    nasdaq = pd.read_csv("nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", sep="|")
    while True:
        stock_picker(nasdaq['Symbol'])
