from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
def rfr(data):
    data['Future Close'] = data['Close'].shift(-1)
    data.drop(len(data) - 1, inplace=True)
    data = data.reset_index()
    X_data = data.drop(['Future Close','TimeStamp'],axis=1)
    y_data = data['Future Close']

    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_data,y_data)
    y_pred = regressor.predict(X_data)
    import matplotlib.pyplot as plt
    # print(X_test['Close'])
    for index in X_data['index']:
        if data.iloc[index]['Open'] > data.iloc[index]['Close']:
            color = 'red'
        elif data.iloc[index]['Open'] <= data.iloc[index]['Close']:
            color = 'green'
        plt.plot([index, index], [data.iloc[index]['Low'], data.iloc[index]['High']], color=color, linewidth=.01)
        plt.plot([index, index], [data.iloc[index]['Open'], data.iloc[index]['Close']], color=color, linewidth=1)
    # plt.scatter(X_data['index'], y_data, color='darkorange', label='data')
    plt.plot(X_data['index'], y_pred, color='navy', lw=.7, label='prediction')
    plt.xlabel("Time")
    plt.ylabel("Target")
    plt.title("Random Forest Regressor")
    plt.legend()
    plt.show()
def display(data):
    fig, axs = plt.subplots(10, 10, figsize=(5, 7))
    index = 0
    for row in range(10):
        for col in range(10):
            color = ""
            if data.iloc[index]['Open'] > data.iloc[index]['Close']:
                color = 'red'
            elif data.iloc[index]['Open'] <= data.iloc[index]['Close']:
                color = 'green'
            axs[row][col].plot([index, index], [data.iloc[index]['Low'], data.iloc[index]['High']], color=color, linewidth=1)
            axs[row][col].plot([index, index], [data.iloc[index]['Open'], data.iloc[index]['Close']], color=color, linewidth=10)
            color = ""
            if data.iloc[index+1]['Open'] > data.iloc[index+1]['Close']:
                color = 'red'
            elif data.iloc[index+1]['Open'] <= data.iloc[index+1]['Close']:
                color = 'green'


            axs[row][col].plot([index+1, index+1], [data.iloc[index+1]['Low'], data.iloc[index+1]['High']], color=color,
                     linewidth=1)
            axs[row][col].plot([index+1, index+1], [data.iloc[index+1]['Open'], data.iloc[index+1]['Close']], color=color,
                     linewidth=10)
            index+=1
    plt.subplots_adjust(hspace=1, wspace=1)
    plt.show()
def train_past_day():
    from Algo_BackTest import process_data
    import requests
    from KeyUpdater import headers
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/TSLA"
    params = {
        'unit': 'Minute',
        "interval": 1,
        'firstdate': "2023-09-13T00:00:00Z",
        'lastdate': "2023-09-15T00:00:00Z"
    }
    response = requests.request("GET", url, params=params, headers=headers())
    print(response.text)
    bars = response.json()['Bars']
    print(process_data(bars))
    data = process_data(bars)
    data['Future Close'] = data['Close'].shift(-1)
    data.drop(len(data) - 1, inplace=True)
    data = data.reset_index()
    X_data = data.drop(['Future Close', 'TimeStamp'], axis=1)
    y_data = data['Future Close']
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_data, y_data)
    url = f"https://api.tradestation.com/v3/marketdata/barcharts/TSLA"
    params = {
        'unit': 'Minute',
        "interval": 1,
        'firstdate': "2023-09-15T00:00:00Z",
        'lastdate': "2023-09-16T00:00:00Z"
    }
    response = requests.request("GET", url, params=params, headers=headers())
    # print(response.text)
    bars = response.json()['Bars']
    print(process_data(bars))
    data = process_data(bars)
    data['Future Close'] = data['Close'].shift(-1)
    data.drop(len(data) - 1, inplace=True)
    data = data.reset_index()
    X_data = data.drop(['Future Close', 'TimeStamp'], axis=1)
    y_data = data['Future Close']
    y_pred = regressor.predict(X_data)
    import matplotlib.pyplot as plt
    # print(X_test['Close'])
    for index in X_data['index']:
        if data.iloc[index]['Open'] > data.iloc[index]['Close']:
            color = 'red'
        elif data.iloc[index]['Open'] <= data.iloc[index]['Close']:
            color = 'green'
        plt.plot([index, index], [data.iloc[index]['Low'], data.iloc[index]['High']], color=color, linewidth=.01)
        plt.plot([index, index], [data.iloc[index]['Open'], data.iloc[index]['Close']], color=color, linewidth=1)
    # plt.scatter(X_data['index'], y_data, color='darkorange', label='data')
    plt.plot(X_data['index']+1, y_pred, color='navy', lw=.7, label='prediction')
    plt.xlabel("Time")
    plt.ylabel("Target")
    plt.title("Random Forest Regressor")
    plt.legend()
    plt.show()
if __name__ == '__main__':
    train_past_day()