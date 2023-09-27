import yfinance as yf
import json
# look for stock gainers in premarket
# looks for a news source
# then buy with a large trailling stop
print(yf.Ticker('RNAZ').news)