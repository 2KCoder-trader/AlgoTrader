# Make a it trade per minute
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
h = datetime.now()-timedelta(days= 5)
import math


def mean_reversion(tick,short_min,long_min,flip):
    sum = 0
    dates = yf.Ticker(tick).history(period='1mo')
    for date in dates.index[2:]:
        off_date = datetime(date.year,date.month,date.day)
        history = yf.Ticker(tick).history(start = off_date,end= off_date+timedelta(days = 1),period = '1d',interval = '1m')
        long_ma = list()
        short_ma = list()
        postion = False
        buy_price = 0
        score = 0
        for x in range(len(history['Open'])):
            price = history.iloc[x]['Open']
            if len(short_ma)>short_min:
                short_ma.pop(0)
            if len(long_ma)>long_min:
                long_ma.pop(0)
            short_ma.append(price)
            long_ma.append(price)
            if flip == True:
                if (np.mean(short_ma) < np.mean(long_ma)) and postion == False:
                    postion = True
                    buy_price = price
                if (np.mean(short_ma) > np.mean(long_ma)) and postion == True:
                    postion = False
                    sell_price = price
                    score += (sell_price-buy_price)
        print(str(date)+": "+str(score))
        sum += score
    print("Flip: "+str(flip)+" Short: "+str(short_min)+" Long: "+str(long_min)+" Score: "+str(sum))
if __name__ == '__main__':
    mean_reversion("CLU23.NYM", 5, 20,True)
