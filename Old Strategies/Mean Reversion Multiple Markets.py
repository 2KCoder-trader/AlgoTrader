# Make a it trade per minute
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
h = datetime.now()-timedelta(days= 5)
import math

# Test with 


def mean_reversion(tick, short_min,long_min,flip,dates):
    postion = False
    buy_price = 0
    score = 0
    long_ma = list()
    short_ma = list()
    for date in dates.index[2:]:
        off_date = datetime(date.year,date.month,date.day)
        history = yf.Ticker(tick).history(start = off_date,end= off_date+timedelta(days = 1),period = '1d',interval = '1m')
        day_score = 0
        for x in range(len(history['Open'])):
            price = history.iloc[x]['Open']
            if len(short_ma)>short_min:
                short_ma.pop(0)
            if len(long_ma)>long_min:
                long_ma.pop(0)
            short_ma.append(price)
            long_ma.append(price)
            if (np.mean(short_ma) < np.mean(long_ma)) and postion == False:
                postion = True
                buy_price = price
            if (np.mean(short_ma) > np.mean(long_ma)) and postion == True:
                postion = False
                sell_price = price
                score += (sell_price-buy_price)
                day_score += (sell_price-buy_price)
        print(f"Day {date}: {day_score}")
        print(f"Accumulating {date}: {score}")





if __name__ == "__main__":
    future  = "CLV23.NYM"
    forex = "EURUSD=X"
    crypto = "BTC-USD"

    short = 1
    long = 2
    for tick in [future,forex,crypto]:
        print(f"Market: {tick}")
        dates = yf.Ticker(tick).history(period='1mo')
        mean_reversion(tick, short, long, True, dates)

