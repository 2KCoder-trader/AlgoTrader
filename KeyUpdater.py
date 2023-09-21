import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
global access_token
def get_access_token():
    limit = datetime.now()
    while True:
        time.sleep(1)
        present = datetime.now()
        if present > limit:
            secrets = pd.read_csv("secrets.csv")
            CLIENT_ID = secrets["Client ID"][0]
            CLIENT_SECRET = secrets["Client Secret"][0]
            REFRESH_TOKEN = secrets["Refresh Token"][0]
            url = "https://signin.tradestation.com/oauth/token"
            payload = f'grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response_data = response.json()
            limit = datetime.now() + timedelta(minutes=19)
            pd.DataFrame([response_data['access_token']],columns=["token"]).to_csv("C:\\Users\\kaide\\OneDrive\\AlgoTrader\\access_token.csv")
def headers():
    token = pd.read_csv("C:\\Users\\kaide\\OneDrive\\AlgoTrader\\access_token.csv").iloc[0]["token"]
    return { "Authorization": f'Bearer {token}'}
if __name__ == '__main__':
    get_access_token()