

def AccountsSim():
    import smtplib
    from email.message import EmailMessage
    import pandas as pd
    import pytz
    import AlgoSimulated
    import requests
    import subprocess
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


    status = False
    tz = pytz.timezone('UTC')
    unsettled_dur = 0
    day_profit = 0
    while True:
        if status != AlgoSimulated.market_status()[0]:
            status = AlgoSimulated.market_status()[0]
            command = "pip install yfinance --upgrade"
            try:
                result = subprocess.check_output(command, shell=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
            if AlgoSimulated.market_status()[0] == False:
                unsettled_dur += 1
                accounts = pd.read_csv("accounts.csv")
                trade_balance = accounts['balance'].sum() / 3
                pd.DataFrame([trade_balance]).to_csv("trade_balance.csv")
                balance = accounts['balance'][0]
                response = requests.request("GET", AlgoSimulated.position_url, headers=AlgoSimulated.headers)
                for position in response.json()['Positions']:
                    day_profit += float(position['RealizedProfitLoss'])
                email_alert("AlgoTrader", f"Balance: {balance}", "8582203752@mailmymobile.net")
                if unsettled_dur == 3:
                    acc_total = accounts['balance'].sum()
                    for i in range(len(accounts)):
                        perc = accounts[i]['balance']/acc_total
                        accounts.loc[i,'balance'] = accounts['balance'][i]+(perc * day_profit)
                    unsettled_dur = 0
                    day_profit = 0
def get_balance():
    import pandas as pd
    accounts = pd.read_csv("accounts.csv")
    return accounts['balance'].sum() / 3


