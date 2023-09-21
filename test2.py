import time

import requests
from KeyUpdater import headers
import json
import re
from datetime import datetime
url = "https://api.tradestation.com/v2/stream/tickbars/TSLA/5/5"

response = requests.request("GET", url, headers=headers(), stream=True)
cur_date = datetime.now()
# collect data
for line in response.iter_lines():
    if line:
        print(line)
        # numbers = re.findall(r'\d+', json.loads(line)['TimeStamp'])
        # timestamp = int(numbers[0]) / 1000
        # date = datetime.fromtimestamp(timestamp)
        # if cur_date == date:
        #     continue
        # cur_date = date
        # print(date)
# run method