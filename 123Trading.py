import multiprocessing

tick = 'MSFT'
    multiprocessing.freeze_support()
    multiprocessing.Process(target=get_access_token).start()
    url = "https://api.tradestation.com/v3/marketdata/barcharts/MSFT"
    params = {
        'interval': str(5),
        'unit': 'Minute',
        'barsback':4
    }
    response = requests.request("GET", url, headers=headers(), params=params)
    bars = response.json()['Bars']
    buy_action = ""
    sell_action = ""
    trade_entry = ""
    bars = __import__("Algo - BackTest").process_data(bars)
    if (bars[0]['High'] > bars[1]['High']) or (bars[0]['High'] > bars[2]['High']):
        if bars[1]['High'] < bars[2]['High']:
            buy_action = 'SELLSHORT'
            sell_action = 'BUYTOCOVER'
            trade_entry = bars[1]['High']
    elif (bars[0]['Low'] < bars[1]['Low']) or (bars[0]['Low'] < bars[2]['Low']):
        if bars[1]['Low'] > bars[2]['Low']:
            buy_action = 'BUY'
            sell_action = 'SELL'
            trade_entry = bars[1]['High']
        payload = {
            "AccountID": "SIM1145924M",
            "Symbol": tick,
            "Quantity": "1",
            "OrderType": "Limit",
            "LimitPrice": str(bars[1]['High']),
            "TradeAction": buy_action,
            "TimeInForce": {
                "Duration": "IOC"
            },
            "Route": "Intelligent",
            "OSOs": [
                {
                    "Type": "BRK",
                    "Orders": [
                        {
                            "AccountID": "SIM1145924M",
                            "Symbol": tick,
                            "Quantity": "1",
                            "OrderType": "Limit",
                            "LimitPrice": str(bars[1]['High']-(.02*(bars[1]['High']))),
                            "TradeAction": sell_action,
                            "TimeInForce": {
                                "Duration": "DAY"
                            },
                            "Route": "Intelligent"
                        },
                        {
                            "AccountID": "SIM1145924M",
                            "Symbol": tick,
                            "Quantity": "1",
                            "OrderType": "StopMarket",
                            "TradeAction": sell_action,
                            "TimeInForce": {
                                "Duration": "GTC"
                            },
                            "Route": "Intelligent",
                            "AdvancedOptions": {
                                "TrailingStop": {
                                    "Percent": "3.0"
                                }
                            }
                        }
                    ]
                }
            ]
        }
        url = "https://sim-api.tradestation.com/v3/orderexecution/orderconfirm"
        response = requests.request("POST", url, json=payload, headers=headers())
        print(response.text)