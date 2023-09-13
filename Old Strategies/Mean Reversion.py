# Make a it trade per minute
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
h = datetime.now()-timedelta(days= 5)
import math

# Test with 


def mean_reversion(tick, short_min,long_min,flip,dates):
    sum = 0
    buy_price = 0
    score = 0
    long_ma = list()
    short_ma = list()
    postion = False
    for date in dates.index[2:]:
        off_date = datetime(date.year,date.month,date.day)
        history = yf.Ticker(tick).history(start = off_date,end= off_date+timedelta(days = 1),period = '1d',interval = '1m')
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
            if flip == False:
                if (np.mean(short_ma) > np.mean(long_ma)) and postion == False:
                    postion = True
                    buy_price = price
                if (np.mean(short_ma) < np.mean(long_ma)) and postion == True:
                    postion = False
                    sell_price = price
                    score += (sell_price-buy_price)
            # print(str(date)+": "+str(score))
        sum += score
    print("Flip: "+str(flip)+" Short: "+str(short_min)+" Long: "+str(long_min)+" Score: "+str(score))
    return score


from multiprocessing import Pool


def process_iteration(args):
    tick, short, long, f, dates = args
    if f == 0:
        mean_reversion(tick, short, long, True, dates)
    elif f == 1:
        mean_reversion(tick, short, long, False, dates)


if __name__ == "__main__":
    tick  = "MSFT"
    dates = yf.Ticker(tick).history(period='1mo')
    short_range = range(1, 31)
    long_range = range(1, 31)
    f_range = range(2)

    inputs = [(tick, short, long, f, dates) for short in short_range for long in long_range for f in f_range]

    with Pool() as pool:
        scores = pool.map(process_iteration, inputs)
    print(np.max(scores))
