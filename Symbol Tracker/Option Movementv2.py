import yfinance as yf
import pandas as pd
import statistics
import math
import requests
from KeyUpdater import headers
from datetime import datetime

ticker = yf.Ticker("SPY")
pd.options.display.max_columns = 10
pd.options.display.max_rows = 1000

# url = "https://api.tradestation.com/v3/marketdata/barcharts/SPY"
# params = {
#     'barsback': '7700',
#     'unit':'Daily'
# }
#
# response = requests.request("GET", url,params=params, headers=headers())
# print(response)
# print(response.json()['Bars'][:2])
# data = pd.DataFrame(columns=['Date','Open','High','Low','Close','TotalVolume','DownVolume','UpVolume'])
# for bar in response.json()['Bars']:
#     new_row = len(data)
#     data.loc[new_row,'Date'] = datetime.strptime(bar['TimeStamp'],'%Y-%m-%dT%H:%M:%SZ').date()
#     data.loc[new_row,'Open'] = float(bar['Open'])
#     data.loc[new_row,'High'] = float(bar['High'])
#     data.loc[new_row,'Low'] = float(bar['Low'])
#     data.loc[new_row,'Close'] = float(bar['Close'])
#     data.loc[new_row,'TotalVolume'] = int(bar['TotalVolume'])
#     data.loc[new_row,'DownVolume'] = int(bar['DownVolume'])
#     data.loc[new_row,'UpVolume'] = int(bar['UpVolume'])
# data.to_csv('SPY.csv',index_label=False)
data = pd.read_csv('SPY.csv')
last_30 = data[-30:]
print(last_30)
spread = list()
for index in range(len(last_30)):
    high_move = abs(last_30.iloc[index]['Open'] - last_30.iloc[index]['High'])/last_30.iloc[index]['Open']
    low_move = abs(last_30.iloc[index]['Open'] - last_30.iloc[index]['Low'])/last_30.iloc[index]['Open']
    if high_move > low_move:
        spread.append(high_move)
    else:
        spread.append(low_move)






# 75% of the time the SPY will travel less than 1% most of the time
def calc_spread(perc, strike):
    movement = strike * perc
    print(str((strike - movement)) + " | " + str(strike) + " | " + str((strike + movement)))


# spread(.0087,449)
import numpy as np
# Your list of numerical values


# Calculate and display percentiles
percentiles = [0,10,20,30,40,50, 60, 70, 80, 90,100]  # You can change these values as needed
for p in percentiles:
    percentile_value = np.percentile(spread, p)
    print(f"{p}th percentile: {percentile_value}")
calc_spread(.0071, 450)
print(1/445)
