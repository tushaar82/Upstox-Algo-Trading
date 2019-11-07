
#Schedule it to run every morning 8:45 AM using CRON Jobs
#The purpose of this file is to generate code and access token 
#Code and Access token is saved in config.ini file
#which later used for Automation.
# Create Log files

from upstox_api.api import *
from datetime import datetime, time
from datetime import timedelta
import time as sleep
import os
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from pyvirtualdisplay import Display
from configparser import ConfigParser
import logging 
import os.path


# Init of Logger , Create a log folder in current directory

logfilepath = os.getcwd()
logfilename = logfilepath + "/" + "log/" +datetime.now().strftime("%Y-%m-%d") + "-"+"Setup.log"
logging.basicConfig(filename = logfilename , 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.INFO)

# INITIALISED LOGGER

logger.info("Logger Initialised")

#Init of config.ini to read parameters

configur = ConfigParser() 
configur.read('config.ini')

logger.info("config.ini Initialised")

#Reading Values from config.ini  

ApiKey = configur.get('upstox','apikey')
ApiSecret = configur.get('upstox','apisecret')
RedirectURL = configur.get('upstox','redirectURL')
DriverPath = configur.get('selenium','chromedriver')
UserName = configur.get('upstox','username')
Password = configur.get('upstox','password')
Pin = configur.get('upstox','pin')

#Start Virtual Display and set resolution


display = Display(visible=0, size=(1024, 768)) 
display.start()

# init Browser and ChromeDriver

browser = webdriver.Chrome(DriverPath)

logger.info("Web Driver Initialised")

# Delete cache and cookies
browser.delete_all_cookies()
logger.info("Cookies Deleted")


s = Session(ApiKey)
s.set_redirect_uri(RedirectURL)
s.set_api_secret(ApiSecret)

#Generate Url for login

generatedUrl = s.get_login_url()
print(generatedUrl)

logger.info("URL Generated")
logger.info("URL: %s", generatedUrl)

# Selenium Automation to Login and Accept Terms & COnditions

browser.get(generatedUrl)

logger.info("Upstox Login Page Opened")

inputElement = browser.find_element_by_xpath('//*[@id="name"]')
inputElement.send_keys(UserName)
logger.info("Upstox Use Name Entered")

passElement = browser.find_element_by_xpath('//*[@id="password"]')
passElement.send_keys(Password)
logger.info("Upstox Password Entered")

pinElement = browser.find_element_by_xpath('//*[@id="password2fa"]')
pinElement.send_keys(Pin)
logger.info("Upstox Pin Entered")

sleep.sleep(5)
elem = browser.find_element_by_xpath('/html/body/form/fieldset/div[3]/div/button')
elem.click()
logger.info("Upstox Login Button Clicked")

sleep.sleep(5)
acceptbtn = browser.find_element_by_xpath('//*[@id="allow"]')
acceptbtn.click()
logger.info("Upstox Accept Button Clicked")

#Delay is necessary because it takes time to generate code

sleep.sleep(100)

# Copy URL to Variable
codelink = browser.current_url
print(codelink)
code = codelink[23:] # Extract COde from URL
print(code)
#8) Wait for 20 secs
sleep.sleep(50)

logger.info("Upstox Code Generated---: %s",code)

s.set_code (code)
access_token = s.retrieve_access_token() 

logger.info("Upstox Access Token Generated---: %s",access_token)

#write code and access token in config file

configur['upstox']['code'] = code
configur['upstox']['accesstoken'] = access_token

with open('config.ini', 'w') as configfile:
 configur.write(configfile)

logger.info("Code and Access Token Writtin in config.ini file")

display.stop()

logger.info("Display Driver Exited")
broswer.quit()

logger.info("Browser  Exited")
