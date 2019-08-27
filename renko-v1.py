"""
Created on Thu June 6  08:45:35 2019
@author: Tushar Chaudhari
"""
# Importing Packages

from upstox_api.api import *
from datetime import datetime, time
from datetime import timedelta
import time as sleep
import os
import pandas as pd
import numpy as np
from pyti.relative_strength_index import relative_strength_index as rsi
from pyti.exponential_moving_average import exponential_moving_average as ema
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from stocktrends import indicators
from talib import EMA

#Opening two TXT files here to write log
#WRITING LOG TO TXT FILES-- SPECIFY URL FOR log.txt and execution.txt

#log = open("D:\\ROBOT-PROJECT\\log\\log.txt", "w")
#execution = open("D:\\ROBOT-PROJECT\\log\\execution.txt", "w")

# Specify Lot Size
quantity = 1

# WRITE IN EXECUTION.TXT
#execution.write("Script | Buy or sell | Price | Stoploss | Square off \n")

# USER AUTHENTICATION AND CODE GENERATION

api_key = "azXcF6EDAu9rpifZGRn8X2dqyWvCna9f7cX9INHb"
api_secret = "xm3bmqmwd7"
redirect_uri = "http://127.0.0.1"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(" GENERATE CODE BY OPENING LINK BELOW")
#print(s.get_login_url())


code = "32e76465f8acefff449e6476b6c9258bc3c35eb5" #---copy code here
s.set_code (code)

#access_token = s.retrieve_access_token()
access_token = "de70647a2c080c3747c414ba32fd458fc29c8975"
print("ACCESS TOKEN GENERATED")
print(access_token)

u = Upstox (api_key, access_token) 

print("Login successful. Verify profile:")
print(u.get_profile())

#log.write("\n" % u.get_profile())

# GET CONTRACTS FOR NSE

master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ

#Function to fetch the current available balance:
def CheckBalance():
    balance = pd.DataFrame(u.get_balance())
    balance1 = balance["equity"]["available_margin"]
    return balance1


#function to fetch historic data and calculation of dataframes
def historicData(script, start_dt, end_dt):
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_5,
                      datetime.strptime(start_dt, "%d/%m/%Y").date(),
                      datetime.strptime(end_dt, "%d/%m/%Y").date()))
    data = data.tail(5)
    #change the name timestamp to date
    data = data[['timestamp','open','high','low','close']]
    data = data.rename({'timestamp': 'date'}, axis=1)
    #convert timestamp into date
    data['date'] = pd.to_datetime(data['date'],unit='ms')
    #convert to float
    data['open'] = data['open'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)
    data['close'] = data['close'].astype(float)
    data = data.reset_index()
    renko = indicators.Renko(data)
    renko.brick_size = 1
    renko.chart_type = indicators.Renko.PERIOD_CLOSE
    renkodata = renko.get_ohlc_data()
    
    renkodata['moving'] = EMA(renkodata['close'], timeperiod=10)
    renkodata['moving'] = renkodata['moving'].astype(float)
    #print(renkodata.tail(5))
    renkodata = renkodata.reset_index()
    return renkodata

#function to check loss
def IsLoss(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    realized = position.loc[position["realized_profit"]<-6]["symbol"].tolist()
    if stock not in realized or not realized:
        return True
    elif stock in realized:
        print("We have already took loss in %s not buying again" %stock)
        #log.write("We have already took loss in %s not buying again" %stock)
        return False

#function to check sell position
def CheckPositionSell(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    bought = position.loc[position["net_quantity"] > 0]["symbol"].tolist()
    if stock not in bought or not bought:
        return True
    elif stock in bought:
        print("There is already a long position on %s, so not selling" %stock)
        #log.write("There is already a long position on %s, so not selling" %stock)
        return False

#function to check buy position
def CheckPositionBuy(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    sold = position.loc[position["net_quantity"] < 0]["symbol"].tolist()
    if stock not in sold or not sold:
        return True
    elif stock in sold:
        print("There is already a short position on %s, so not buying" %stock)
        #log.write("There is already a short position on %s, so not buying" %stock)
        return False

#BUY FUNCTION

def buy(script):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    price = float(cp['ltp'])
    print("Buying")
    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 quantity,  # quantity
                 OrderType.Market,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 price,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 None,  # stop_loss
                 None,  # square_off
                 20)  # trailing_ticks 20 * 0.05

#sell function

def sell(script):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    price = float(cp['ltp'])
    print("Selling ")
    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 quantity,  # quantity
                 OrderType.Market,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 price,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 None,  # stop_loss
                 None,  # square_off
                 20)  # trailing_ticks 20 * 0.05

 

def RenkoStrategy(ScriptData,script):
    if ScriptData.uptrend.iloc[-2] == 'False' and ScriptData.uptrend.iloc[-1] == 'True':
        if CheckPositionBuy(script):
            #u.cancel_all_orders()
            sleep.sleep(5)
            buy(script)

    if ScriptData.uptrend.iloc[-2] == 'True' and ScriptData.uptrend.iloc[-1] == 'False':
        if CheckPositionBuy(script):
            #u.cancel_all_orders()
            sleep.sleep(5)
            sell(script)
#%%
def CheckTrades():
    now = datetime.now()
    now_time = now.time()
    end_dt = datetime.now().strftime("%d/%m/%Y")
    start_dt = (datetime.now() - timedelta(3)).strftime('%d/%m/%Y')

    if time(9,15) <= now_time <= time(14,15) and CheckBalance() > 500:
        bucket1 = ["SBIN"]
        bucket2 = ["IOC", "NTPC", "ONGC", "TATAMOTORS", "POWERGRID", "VEDL", "HINDALCO", "COALINDIA", "HINDPETRO"]

        for script in bucket1:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            
            print("Checking for RSI Parameters for %s" % script)
            
            
            RenkoStrategy(historicData(script, start_dt, end_dt), script)
          
        for script2 in bucket2:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            #log.write("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            print("Checking for RSI Parameters for %s" % script2)
            #log.write("Checking for RSI Parameters for %s" % script2)
            RenkoStrategy(historicData(script, start_dt, end_dt), script)
            
    elif time(14,58) <= now_time <= time(15,00):
        print("Exiting all the open position now and exiting execution")
        #log.write("Exiting all the open position now and exiting execution")
        u.cancel_all_orders() #Cancel all open orders
        #log.close()
        #execution.close()
        exit()

    else:
        print("There is no market activity now. Checking in 2 mins.. Now the time is: %s" % datetime.now().time())
        #log.write("There is no market activity now. Checking in 2 mins.. Now the time is: %s" % datetime.now().time())
        sleep.sleep(120)

#%%
while True:
    CheckTrades()
    print("\n***Now waiting for 65 seconds")
    #log.write("\n***Now waiting for 320 seconds")
    sleep.sleep(900)
