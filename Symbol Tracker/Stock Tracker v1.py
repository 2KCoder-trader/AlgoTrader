import multiprocessing
import smtplib
from email.message import EmailMessage

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


def stock_check(sym):
    try:
        info_sym = yf.Ticker(sym)
    except Exception as e:
        print(sym, e)
        return
    try:
        if info_sym.info['floatShares'] >= 100000000:
            print(sym, " High Float Share Number")
            return

    except Exception:
        try:
            if info_sym.info['sharesOutstanding'] >= 100000000:
                print(sym, " High Outstanding Share Number")
                return

        except Exception:
            print(sym, " Cant Find Outstanding Share Number")
            return

    try:
        bars = info_sym.history(period='1d', interval="1m")
    except Exception:
        print(sym," Cannot Find Price Data")
        return

    vol1 = bars.iloc[-2]["Volume"]
    vol0 = bars.iloc[-3]["Volume"]
    col1 = bars.iloc[-1]["Close"]
    col0 = bars.iloc[-2]["Close"]
    # if coln1 >= col0:
    #     print(sym, " No Price increase, ", col0, " ", coln1)
    #     return
    if vol0*2 >= vol1:
        print(sym, " No Volume Increase",vol0," ",vol1)
        return
    if vol1 < 1000:
        print(sym, " Not High Enough Volume")
        return


    moving_average = bars.iloc[-20:]['Close'].mean()

    if moving_average >= bars.iloc[-1]['Close']:
        print( sym, " Close Price is Under Moving Average",moving_average," ",bars.iloc[-1]['Close'])
        return

    ma = moving_average
    cur_close = bars.iloc[-1]['Close']
    print('Good Symbol: ', sym, '\n',
            "Previous Volume ", vol0, '\n',
            "Current Volume ", vol1, '\n',
            "Moving Average ", ma, '\n',
            "Current Close ", cur_close)
    return
    # email_alert("Active Stock",sym,"8582203752@mailmymobile.net")


if __name__ == '__main__':
    # Need to run KeyUpdater for this to work
    while True:
        # if market_status()[0] == True:
        page_to_scrape = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
        file = open("../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", "w")
        file.write(str(page_to_scrape.text))
        file.close()
        nasdaq = pd.read_csv("../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", sep="|")
        nasdaq.drop(len(nasdaq) - 1, axis=0, inplace=True)
        syms = ' '.join(map(str, nasdaq["Symbol"]))
        ticks = yf.Tickers(syms)
        num_cores = multiprocessing.cpu_count()
        chunk_size = len(nasdaq["Symbol"]) // num_cores
        print(nasdaq["Symbol"])
        print(len(nasdaq["Symbol"]))
        print(chunk_size)
        print(num_cores)
        # Split the list of words into smaller chunks for parallel processing
        sym_list = list()
        for i in range(0, len(nasdaq["Symbol"]), chunk_size):
            sym_list.append(list(nasdaq["Symbol"])[i: (i + chunk_size)])
        p_i = 0
        print(len(sym_list))
        print(len(sym_list[0]))
        print(len(sym_list[12]))
        try:
            with multiprocessing.Pool(processes=num_cores) as pool:
                # Use pool.map to apply the method to each chunk in parallel
                print(pool.map(stock_check, list(nasdaq["Symbol"])))
        except Exception:
            pass
