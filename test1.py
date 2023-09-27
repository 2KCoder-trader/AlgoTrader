import pandas as pd
import yfinance as yf
info = yf.Ticker('TSLA').info
print(info['ask'])
print(info['bid'])