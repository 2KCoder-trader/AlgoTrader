import yfinance as yf
import multiprocessing
import AlgoSimulated
import pandas as pd

from KeyUpdater import get_access_token
import requests
import time
sym = ""

# class main:
#     def __init__(self):
#         self.trade_balance = 0
#         self.orders = pd.DataFrame()
#     def get_trade_balance():
#         return globals()['trade_balance']
#
#
#     def set_trade_balance(num):
#         global trade_balance
#         trade_balance = 0
#         globals()['trade_balance'] = num
#
#
#     def remove_trade_balance(num):
#         globals()['trade_balance'] -= num
#
#     def set_orders():
#         global orders
#         globals()['orders'] = pd.DataFrame()
#
#     def get_orders():
#         return globals()['orders']
#
#     def remove_from_orders(i):
#
#         globals()['orders'].drop(i,axis=0,inplace = True)
#         globals()['orders'].reset_index(inplace= True)
#         globals()['orders'].drop(["index"], axis=1, inplace=True)
#
#     def append_to_orders(tick,id):
#         add = pd.DataFrame({"Symbol":tick,"Order Id":id},index=[len(globals()['orders'])])
#         globals()['orders'] = pd.concat([globals()['orders'],add],axis=0)
trade_balance = 0
orders = pd.DataFrame()

# Press the green button in the gutter to run the script.
def stock_picker(ticks):
    for tick in ticks:
        try:
            stock_info = yf.Ticker(tick).info
            if stock_info['previousClose'] > 3:
                continue
            if ('none' == stock_info['recommendationKey']) or (
                    'underperform' == stock_info['recommendationKey']) or (
                    'sell' == stock_info['recommendationKey']):
                continue
            print("Stock is Good: ", tick)
            multiprocessing.Process(target=AlgoSimulated.algoTrader, args=[tick]).start()
            # print("Processors: ", multiprocessing.active_children())
            while len(multiprocessing.active_children()) >= 9:
                # print("Final Orders: ", orders)
                # print(" Final Trade Balance: ", trade_balance)
                pass
        except Exception as e:
            # print("Final Orders: ", orders)
            # print(" Final Trade Balance: ", trade_balance)
            # print("Error occured: ", e)
            pass


if __name__ == '__main__':
    # multiprocessing.Process(target=AccountsSim.AccountsSim).start()
    # multiprocessing.Process(target=Idle).start()
    trade_balance = 4000
    multiprocessing.Process(target=get_access_token).start()
    time.sleep(10)
    # Put the function below in accountsim
    try:
        while True:
            page_to_scrape = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
            file = open("../../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", "w")
            file.write(str(page_to_scrape.text))
            file.close()
            nasdaq = pd.read_csv("../../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", sep="|")
            nasdaq.drop(len(nasdaq) - 1, axis=0, inplace=True)
            stock_picker(nasdaq['Symbol'])
    except Exception:
        print("Final Orders: ", orders)
        print(" Final Trade Balance: ", trade_balance)
    print("Final Orders: ", orders)
    print(" Final Trade Balance: ", trade_balance)


