from itertools import combinations

import numpy as np
import pandas as pd
import requests
from KeyUpdater import headers
from datetime import datetime, timedelta
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)

def reformat_data(df,tick):
    new_df = pd.DataFrame()
    df['Date'] = df['TimeStamp'].apply(lambda x: x.date())
    for date in sorted(list(df['Date'].unique())):
        # print(date)
        date_df = df[df['Date']==date]
        date_df = date_df.sort_values('TimeStamp',ascending=True)
        date_series = pd.Series(list(date_df['Close']),name=tick+str(date))
        new_df = pd.concat([new_df,date_series],ignore_index = True,axis =1)
    return new_df

def SVD(tick):
    # combinations_list = list(combinations(ticks, 2))
    # result = [list(combination) for combination in combinations_list]
    # for tick_pair in result:

    firstdate = (datetime.now()-timedelta(days = 7)).strftime('%Y-%m-%dT00:00:00Z')
    lastdate = (datetime.now()).strftime('%Y-%m-%dT00:00:00Z')
    params = {
        'unit':'Minute',
        'firstdate':str(firstdate),
        'lastdate':str(lastdate),
    }
    # url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick_pair[0]}"
    # response = requests.request("GET", url, params = params, headers=headers)
    # tick_0_df = reformat_data(getattr(__import__("Algo - BackTest"),'process_data')(response.json()['Bars']),tick_pair[0])
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/{tick}"
    response = requests.request("GET", url, params=params, headers=headers())
    # print(response.json())
    tick_1_df = reformat_data(getattr(__import__("Algo - BackTest"), 'process_data')(response.json()['Bars']),tick)
    # print(pd.concat([tick_0_df,tick_1_df],axis=1))
    # print(tick_1_df)
    tick_1_df.dropna(axis = 'columns',inplace=True)
    col_len = len(tick_1_df.columns)
    tick_1_df = tick_1_df[[col_len-2,col_len-1]]
    print(tick_1_df)


    euclidean_norm = np.linalg.norm(tick_1_df, axis=1)
    # print(tick_1_df.loc[0,10])
    # print(euclidean_norm)
    tick_1_df = tick_1_df.divide(euclidean_norm, axis=0)
    # print(tick_1_df)
    tick_1_df = tick_1_df.applymap(lambda x: 1000/x)
#         ^ Input data is completed
    print(tick)
    print(tick_1_df)
    return tick_1_df

