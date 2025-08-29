pip install kiteconnect

from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
import logging
import os
import time
import datetime as dt
api_key = "1ll4p8ziqlk8hh7g"
api_secret = "x59r5u1vd25annfpgts22wv8ykfueirl"
kite = KiteConnect(api_key=api_key)

print(kite.login_url()) #use this url to manually login and authorize yourself

#generate trading session
request_token = "PwoQlLGKjW1XwEZTOA9AReqbIDM2JqJ6" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
data = kite.generate_session(request_token, api_secret=api_secret)
#create kite trading object
kite.set_access_token(data["access_token"])

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
instrument_df.to_csv("NSE_Instruments.csv",index=False)

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1

def fetchOHLC(ticker,interval,duration):
  """extracts historcial data and outputs in the form of dataframe"""
  instrument = instrumentLookup(instrument_df,ticker)
  data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration),dt.date.today(),interval))
  # data1 = pd.DataFrame(kite.historical_data(instrument,dt.date.today(),dt.date.today(),interval))
  # print(data1.head())
  data.set_index("date",inplace=True)
  return data

# List of Nifty 50 constituent trading symbols (update as per latest list)
nifty50_symbols = ["RELIANCE", "HDFCBANK", "BHARTIARTL", "TCS", "ICICIBANK", "SBIN", "INFY", "HINDUNILVR", "BAJFINANCE", "ITC"]
instrument_token = [6401, 40193, 60417, 81153, 98049, 119553, 177665, 225537, 315393, 341249, 345089, 348929, 408065, 424961, 
                    492033, 502785, 519937,  633601, 738561, 779521, 857857, 878593, 884737, 895745, 897537, 969473, 1270529, 
                    1304833, 1346049, 1510401, 1850625, 2815745, 2939649, 2952193, 2953217, 2977281, 3001089, 3465729, 4267265, 
                    4268801, 4598529, 4644609, 5215745, 5582849, 3861249]

def placeMarketOrder(symbol, buy_sell, quantity):
  # place intraday market order on NSE
  if buy_sell == "buy":
    t_type = kite.TRANSACTION_TYPE_BUY
  elif buy_sell == "sell":
    t_type = kite.TRANSACTION_TYPE_SELL
  kite.place_order(tradingsymbol=symbol,
                   exchange=kite.EXCHANGE_NSE,
                   transaction_type=t_type,
                   quantity=5*quantity, # 5x leverage
                   order_type=kite.ORDER_TYPE_MARKET,
                   product=kite.PRODUCT_MIS,
                   variety=kite.VARIETY_REGULAR)

for i in nifty50_symbols:
  df_yesterday = fetchOHLC(i,"5minute", 1)
  #print(i, df)
  df_today = fetchOHLC(i, "5minute", 0)
  capital = 10000 #position size
  quantity = int(capital/df_today["close"][-1])
  close_11am = df_today['close'][-1]
  intraday_high = df_today['high'].max()
  intraday_low = df_today['low'].min()
  instrument = instrumentLookup(instrument_df, i)
  if instrument != -1: # Check if instrument token was found
      yesterday_close = kite.quote([instrument])[str(instrument)]['ohlc']['close'] # Use instrument token as key
  else:
      print(f"Instrument token not found for {i}")
  pivot_price = (intraday_high+intraday_low+yesterday_close)/3
  #print(pivot_price, close_11am) 28.08.2025
  if close_11am > pivot_price:
    print(f"buy {i}")
    #placeMarketOrder(i, "buy", quantity)
  elif close_11am < pivot_price:
    print(f"sell {i}")
    #placeMarketOrder(i, "sell", quantity)
