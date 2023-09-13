import multiprocessing
import smtplib
import subprocess
from email.message import EmailMessage
from datetime import datetime
import pytz
import requests
import pandas as pd
import yfinance as yf

syms = ""


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "kaidenkrenek@gmail.com"
    msg['from'] = user
    password = "iddrljybnnflbyla"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

def white_list(sym):

    try:
        info_sym = yf.Ticker(sym)
        try:
            if info_sym.info['floatShares'] >= 100000000:
                return

        except Exception:
            try:
                if info_sym.info['sharesOutstanding'] >= 100000000:
                    return

            except Exception:
                return
        if info_sym.info["currentPrice"]>=30:
            return
        if info_sym.history(period = '5d').empty:
            return
        return sym
    except Exception:
        return

def news_check(sym):
    try:
        eastern_tz = pytz.timezone('US/Eastern')
        news= yf.Ticker(sym).news
        print(sym)
        lastest_news = news[0]
        utc_dt = datetime.utcfromtimestamp(lastest_news["providerPublishTime"]).replace(tzinfo=pytz.utc)
        eastern_dt = utc_dt.astimezone(eastern_tz)
        formatted_time = eastern_dt.strftime("%Y-%m-%d %H:%M")
        today = datetime.now()
        data_url = "https://api.tradestation.com/v3/marketdata/barcharts/AAPL"
        news_start = datetime(year=today.year, month=today.month, day=today.day, hour=0,minute=0,tzinfo= eastern_tz)
        news_end = datetime(year=today.year, month=today.month, day=today.day, hour=9, minute=30, tzinfo=eastern_tz)

        if len(lastest_news["relatedTickers"])>2:
            return False
        if eastern_dt > news_start and eastern_dt < news_end:
            print(sym, " True")
            return formatted_time

    except Exception:
        return False
    return False





def stock_check(sym):
        info_sym = yf.Ticker(sym)

        bars = info_sym.history(period='1d', interval="1m")
        if bars.empty:
            return "N: ",sym

        vol1 = bars.iloc[-2]["Volume"]
        vol0 = bars.iloc[-3]["Volume"]
        if vol0*2 >= vol1:
            return
        if vol1 < 1000:
            return
        if info_sym.info['currentPrice']>20:
            return
        # week_report = info_sym.history(period='1d', interval="1d")
        # gap_range = week_report.iloc[0]["High"]-week_report.iloc[0]["Low"]
        # if gap_range < week_report.iloc[0]["Close"]*.5:
        #     return

        # moving_average = bars.iloc[-20:]['Close'].mean()
        # if moving_average >= bars.iloc[-1]['Close']:
        #     return


        # ma = moving_average
        # cur_close = bars.iloc[-1]['Close']
        # print('Good Symbol: ', sym, '\n',
        #         "Previous Volume ", vol0, '\n',
        #         "Current Volume ", vol1, '\n',
        #         "Moving Average ", ma, '\n',
        #         "Current Close ", cur_close)
        # print(sym," ", str(100*(gap_range/week_report.iloc[0]["Close"])))
    #     return sym
    # except Exception:

    # email_alert("Active Stock",sym,"8582203752@mailmymobile.net")


if __name__ == '__main__':
    command = "pip install yfinance --upgrade"
    try:
        subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    # # if market_status()[0] == True:
    nasdaq = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
    nyse = requests.get("http://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt")
    file = open("../ticker_list.txt", "w")
    file.write(str(nasdaq.text))
    file.write(str(nyse.text))
    file.close()



    nasdaq = pd.read_csv("../ticker_list.txt", sep="|")
    num_cores = multiprocessing.cpu_count()
    # p = list()
    #
    # white_list(nasdaq["Symbol"][1308])
    # try:
    #     with multiprocessing.Pool(processes=num_cores) as pool:
    #         # Use pool.map to apply the method to each chunk in parallel
    #         p = pool.map(white_list, list(nasdaq["Symbol"]))
    # except Exception:
    #     pass
    # p = [item for item in p if item is not None]
    # print(p)
    # filtered_list = pd.DataFrame(columns = ["Symbol"])
    # filtered_list["Symbol"] = p
    # filtered_list.to_csv("white_list.csv",index = False)
    white_l = pd.read_csv("../white_list.csv", index_col=False)
    today = datetime.now()
    # while datetime.now() < datetime(today.year,today.month,today.day,9,30):
    news = list()
    while True:
        try:
            news_info = yf.Ticker(white_l["Symbol"][0]).news
            break
        except Exception:
            pass
    try:
        with multiprocessing.Pool(processes=num_cores) as pool:
            # Use pool.map to apply the method to each chunk in parallel
            news = pool.map(news_check, list(white_l["Symbol"]))
    except Exception:
        pass
    white_l["News"] = news

    print(white_l[white_l["News"]!=False])
