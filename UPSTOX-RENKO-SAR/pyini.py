from configparser import ConfigParser 
from datetime import datetime, time
from datetime import timedelta
import ast
import logging 
import os.path

configur = ConfigParser() 
configur.read('config.ini')

configur['upstox']['code'] = 'love'
configur['upstox']['accesstoken'] = 'sdsdsdsadas'

# to get boolean value use commented code
#print ("Log Errors debugged ? : ", configur.getboolean('debug','log_errors')) 


print("Api Key---",configur.get('upstox','apikey'))
print("Api Secret----",configur.get('upstox','apisecret'))
print("Redirect URL----",configur.get('upstox','redirectURL'))
print("code----",configur.get('upstox','code'))
print("access token---",configur.get('upstox','accesstoken'))
print ("Stocks to Buy---- ", configur.getint('upstox','stock'))
print("driverpath----",configur.get('selenium','chromedriver'))
print("User Name----",configur.get('upstox','username'))
print("Password----",configur.get('upstox','password'))
print("Pin----",configur.get('upstox','pin'))
print("Holiday Dates----",configur.get('nse','holidays'))
print("Chrome Driver Path----",configur.get('selenium','chromedriver'))


def isholiday():
    holidays = ast.literal_eval(configur.get("nse", "holidays"))
    for holiday in holidays:
       	today_date = datetime.now().strftime("%d/%m/%Y")
        if holiday == today_date:
            return True


print(isholiday())

bucket1 = ast.literal_eval(configur.get("nse", "scrips1"))
for script in bucket1:
	print(script)

bucket2 = ast.literal_eval(configur.get("nse", "scrips2"))
for script in bucket2:
	print(script)


logfilepath = os.getcwd()
logfilename = logfilepath + "/" + "log/" +datetime.now().strftime("%Y-%m-%d") + "-"+"Log.log"
logging.basicConfig(filename = logfilename , 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 
  
#Test messages 
logger.debug("Harmless debug Message") 
logger.info("Just an information") 
logger.warning("Its a Warning") 
logger.error("Did you try to divide by zero") 
logger.critical("Internet is down") 

#with open('config.ini', 'w') as configfile:
# configur.write(configfile)