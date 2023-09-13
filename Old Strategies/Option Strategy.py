# The goal of this strategy is to make as many sell call/put options execution at the last 5 minutes of the market
# Profit per contract will be roughly   1.00 premium - .60 commission = .40 profit
# To allow for more executions to occur the cost toward buying power must be decreased as much as possible
# To lower the buying power cost It believed to target stocks that have a low share price
# stocks expire every Friday
stocks = ["NU"]
from datetime import datetime
from KeyUpdater import headers
import pandas_market_calendars as mcal
import pytz
import datetime as dt
import requests
import json

# Make the program only able to run in between 3:55-4
def market_status():
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=str(dt.date.today()), end_date=str(dt.date.today()))
    if schedule.empty:
        return False
    else:
        if schedule['market_open'][0] > datetime.now(pytz.utc):
            return False
        elif schedule['market_close'][0] < datetime.now(pytz.utc):
            return False
        else:
            return True

while True:
            today = datetime.now()
            if (market_status()) and (today.weekday() == 4) and (datetime(today.year, today.month, today.day, 15, 55) < today < \
                    datetime(today.year, today.month, today.day, 16, 0)):

                url = "https://sim-api.tradestation.com/v3/marketdata/stream/options/chains/NU"
                params = {
                    "expiration": str(datetime.now().strftime("%m-%d-%y")),
                    "strikeProximity": 20,
                }
                response = requests.request("GET", url, headers=headers(),params=params, stream=True)

                for line in response.iter_lines():
                    if line:
                        formatted_line = json.loads(line)
                        if (float(formatted_line["ProbabilityOTM"]) > .9) and (float(formatted_line["Bid"]) >= .01):
                            symbol = formatted_line['Legs'][0]["Symbol"]
                            payload = {
                                "AccountId": "SIM1145924M",
                                "Symbol": "NU",
                                "OrderType": "Market",
                                "Route": "Intelligent",
                                "TimeInForce": {"Duration": "DAY"},
                                "Route": "Intelligent",
                                "Legs": [
                                    {
                                        "Symbol": f"{symbol}",
                                        "Quantity": "1",
                                        "TradeAction": "SellToOpen"
                                    }
                                ]
                            }
                            url = "https://sim-api.tradestation.com/v3/orderexecution/orders"
                            response = requests.request("POST", url, json=payload, headers=headers())
                            end = False
                            for key in formatted_line.keys():
                                if key == "Heartbeat":
                                    end = True
                                    break
                            if end:
                                break
            else:
                continue
