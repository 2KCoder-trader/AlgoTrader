import multiprocessing
import smtplib
import subprocess
from email.message import EmailMessage
from datetime import datetime, timedelta
import pytz
import requests
import pandas as pd
import yfinance as yf
import numpy as np

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


def filter_list(sym):
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
        if info_sym.info["currentPrice"] >= 50:
            return
        graph_data = yf.download(sym, start=datetime.now() - timedelta(days=3), prepost=True, interval='1m',
                                 progress=False)
        if graph_data.empty:
            return
        return sym
    except Exception:
        return


def refresh_list():
    nasdaq = requests.get("http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt")
    nyse = requests.get("http://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt")
    file = open("../ticker_list.txt", "w")
    file.write(str(nasdaq.text))
    file.write(str(nyse.text))
    file.close()
    nasdaq = pd.read_csv("../ticker_list.txt", sep="|")
    num_cores = multiprocessing.cpu_count()
    p = list()
    try:
        with multiprocessing.Pool(processes=num_cores) as pool:
            # Use pool.map to apply the method to each chunk in parallel
            p = pool.map(filter_list, list(nasdaq["Symbol"]))
    except Exception:
        pass
    p = [item for item in p if item is not None]
    filtered_list = pd.DataFrame(columns=["Symbol"])
    filtered_list["Symbol"] = p
    filtered_list.to_csv("filtered_list.csv", index=False)


def trigger(tick):
    try:

        graph_data = yf.download(tick, start=datetime.now() - timedelta(days=5), prepost=True, interval='1m',
                                 progress=False)
        prev_std_deviation = np.std(graph_data['Close'][-100:-1])
        std_deviation = np.std(graph_data['Close'][-100:])
        # if abs((std_deviation - prev_std_deviation)) < .005:
        #     return [tick,0]
        info = yf.Ticker(tick).info
        rel_vol = info['volume'] / info['averageVolume10days']
        score = round(
            (((graph_data['Close'].iloc[-1] - graph_data['Close'][-100:].mean()) / graph_data['Close'].iloc[-1]) * 100),
            3)
        return [tick, rel_vol, score]
    except Exception:
        return [tick, 0, 0]


if __name__ == '__main__':
    command = "pip install yfinance --upgrade"
    try:
        subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    refresh_list()
    num_cores = multiprocessing.cpu_count()
    filtered_list = pd.read_csv("filtered_list.csv", index_col=False)
    while True:
        try:
            with multiprocessing.Pool(processes=num_cores) as pool:
                scores = pool.map(trigger, list(filtered_list["Symbol"]))
        except Exception:
            pass
        score_data = pd.DataFrame(columns=["Symbol", "Relative Volume", "Gap"])
        for score in scores:
            new_score_df = pd.DataFrame([score], columns=score_data.columns)
            score_data = pd.concat([score_data, new_score_df], ignore_index=True)
        print(datetime.now())
        print(score_data.sort_values("Relative Volume", ascending=False).head(20))
