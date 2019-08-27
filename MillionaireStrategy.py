# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 10:29:35 2018

@author: Tushaar Chaudhari

"""

# IMPORTING PACKAGAES

from upstox_api.api import *
from datetime import datetime, time
import time as sleep
import os
import pandas as pd

#%%
#Opening two TXT files here to write log
log = open("D:\\Upstox\\log\\log.txt", "w")
execution = open("D:\\Upstox\\log\\execution.txt", "w")

quantity = 3 # stock quantity to buy

#Creating header for execution:
execution.write("Script | Buy or sell | Price | Stoploss | Square off \n")

#%% UPSTOX AUTHETICATION
##enter api_key and api_secret to get access token and authenticate our requests

api_key = "api_key"
api_secret = "api_secret"
redirect_uri = "http://127.0.0.1"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(s.get_login_url())
code = "Code"

s.set_code (code)
access_token = s.retrieve_access_token()

u = Upstox (api_key, access_token)

print("Login successful. Verify profile:")
log.write("\nLogin successful. Verify profile:")
print(u.get_profile())
log.write("\n" % u.get_profile())

#%%
master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ
