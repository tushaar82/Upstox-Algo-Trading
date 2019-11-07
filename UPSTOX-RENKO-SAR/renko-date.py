
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
from configparser import ConfigParser

# Open Config File

configur = ConfigParser() 
configur.read('config.ini')

# Extract Stock Quantity from config.ini

quantity = configur.getint('upstox','stock')

# get code and access token from txt file save by setup.py

ApiKey = configur.get('upstox','apikey')
AccessToken = configur.get('upstox','accesstoken')

# Initialise Upstox Object

u = Upstox (ApiKey, AccessToken) 

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

# Function to know wetherr today is holiday or not
#if it is holiday function returns True
# if it is not holiday function returns None
def isholiday():
    holidays = ast.literal_eval(configur.get("nse", "holidays"))
    for holiday in holidays:
        today_date = datetime.now().strftime("%d/%m/%Y")
        if holiday == today_date:
            return True

#function to fetch historic data and calculation of dataframes
def historicData(script, start_dt, end_dt):
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_15,
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
    renko.brick_size = 0.5
    renko.chart_type = indicators.Renko.PERIOD_CLOSE
    renkodata = renko.get_ohlc_data()  
    renkodata['SAR'] = SAR(renkodata['high'], renkodata['low'], acceleration=0.02, maximum=0.2)
    renkodata['SAR'] = renkodata['SAR'].astype(float)
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
    if ScriptData.SAR.iloc[-2] > ScriptData.open.iloc[-2] and ScriptData.SAR.iloc[-1] < ScriptData.open.iloc[-1]:
            buy(script)

    if ScriptData.SAR.iloc[-2]< ScriptData.open.iloc[-2] and ScriptData.SAR.iloc[-1] > ScriptData.open.iloc[-1]:
            sell(script)

def CheckTrades():
    now = datetime.now()
    now_time = now.time()
    end_dt = datetime.now().strftime("%d/%m/%Y")
    start_dt = (datetime.now() - timedelta(3)).strftime('%d/%m/%Y')

    if time(9,15) <= now_time <= time(14,15) and CheckBalance() > 500 and isholiday() != True:
    	
        bucket1 = ast.literal_eval(configur.get("nse", "scrips1"))
        bucket2 = ast.literal_eval(configur.get("nse", "scrips2"))

        for script in bucket1:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())           
            print("Checking for Renko and SAR Parameters for %s" % script)                        
            RenkoStrategy(historicData(script, start_dt, end_dt), script)

        for script in bucket2:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())           
            print("Checking for Renko and SAR Parameters for %s" % script)                        
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
