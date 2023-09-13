import multiprocessing
import smtplib
import subprocess
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
        try:
            if info_sym.info['floatShares'] >= 100000000:
                return

        except Exception:
            try:
                if info_sym.info['sharesOutstanding'] >= 100000000:
                    return

            except Exception:
                return

        bars = info_sym.history(period='1d', interval="1m")
        if bars.empty:
            raise

        vol1 = bars.iloc[-2]["Volume"]
        vol0 = bars.iloc[-3]["Volume"]
        if vol0*2 >= vol1:
            return
        if vol1 < 1000:
            return


        moving_average = bars.iloc[-20:]['Close'].mean()
        if moving_average >= bars.iloc[-1]['Close']:
            return

        ma = moving_average
        cur_close = bars.iloc[-1]['Close']
        # print('Good Symbol: ', sym, '\n',
        #         "Previous Volume ", vol0, '\n',
        #         "Current Volume ", vol1, '\n',
        #         "Moving Average ", ma, '\n',
        #         "Current Close ", cur_close)
        print(sym)
        return sym
    except Exception:
        return

    # email_alert("Active Stock",sym,"8582203752@mailmymobile.net")


if __name__ == '__main__':
    command = "pip install yfinance --upgrade"
    try:
        subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    while True:
        # if market_status()[0] == True:
        page_to_scrape = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
        file = open("../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", "w")
        file.write(str(page_to_scrape.text))
        file.close()
        nasdaq = pd.read_csv("../nasdaqtrader.com_dynamic_SymDir_nasdaqlisted.txt", sep="|")
        nasdaq.drop(len(nasdaq) - 1, axis=0, inplace=True)
        syms = ' '.join(map(str, nasdaq["Symbol"]))
        num_cores = multiprocessing.cpu_count()
        p = list()
        try:
            with multiprocessing.Pool(processes=num_cores) as pool:
                # Use pool.map to apply the method to each chunk in parallel
                p = pool.map(stock_check, list(nasdaq["Symbol"]))
        except Exception:
            pass
        p = [item for item in p if item is not None]
        message = ""
        for sym in p:
            message += sym+ "\n"
        email_alert("Watch List:",message,"kaidenkrenek@gmail.com")
