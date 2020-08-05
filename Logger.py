import calendar
import os
import platform
import sys
import urllib.request
import time
from tqdm import tqdm

import json
import pickle
import re 

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

'''
		

		Logger class : 	--SINGLETON-- for MetaLogger
		
			attributes : - driver : Sellenium's chrome driver 
				
						 - credantials : python dictionary loaded from json file 
						 				: {"email":"YOUR EMAIL","password":"YOUR PASSWORD"}
				
						 - platform : Your Platform 


'''	

	

class MetaLogger :
	def __init__(self):
		
		#	Initializing Credencials
		self.credencials = self.read_credencials_file()

		#	Initializing Driver Options
		options = self.set_driver_options()


		try:
			self.platform = platform.system().lower()
		
			if self.platform in ['linux', 'darwin']:
				self.driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
			else:
				self.driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
			self.driver.header_overrides ={'Accept-Language': 'en-US,en;q=0.8'}
		
		except:
			print("Kindly replace the Chrome Web Driver with the latest one from "
				  "http://chromedriver.chromium.org/downloads "
				  "and also make sure you have the latest Chrome Browser version."
				  "\nYour OS: {}".format(this.platform)
				  )
			exit()

	def set_driver_options(self):

		options = Options()

		#  Code to disable notifications pop up of Chrome Browser
		options.add_argument("--disable-notifications")
		options.add_argument("--disable-infobars")
		options.add_argument("--mute-audio")
		# options.add_argument("headless")
		return options

	def read_credencials_file(self , filename='credencials.json'):
		with open(filename) as json_file:
			credencials = json.load(json_file)
			return credencials
			
	def log(self ):
		
		try:
			self.driver.get("https://mbasic.facebook.com")
			self.driver.maximize_window()

			# filling the form
			self.driver.find_element_by_name('email').send_keys(self.credencials['email'])
			self.driver.find_element_by_name('pass').send_keys(self.credencials['password'])

			# clicking on login button
			self.driver.find_element_by_name("login").click()

			# if your account uses multi factor authentication
			mfa_code_input = safe_find_element_by_id(self.driver, 'approvals_code')

			if mfa_code_input is None:
				return

			mfa_code_input.send_keys(input("Enter MFA code: "))
			self.driver.find_element_by_id('checkpointSubmitButton').click()

			# there are so many screens asking you to verify things. Just skip them all
			while safe_find_element_by_id(driver, 'checkpointSubmitButton') is not None:
				dont_save_browser_radio = safe_find_element_by_id(self.driver, 'u_0_3')
				if dont_save_browser_radio is not None:
					dont_save_browser_radio.click()

				self.driver.find_element_by_id('checkpointSubmitButton').click()

		except Exception as e:
			print("There's some error in log in.")
			print(sys.exc_info()[0])
			exit()
	

class Logger():
   __instance = None
   @staticmethod 
   def getInstance():
      """ Static access method. """
      if Logger.__instance == None:
         Logger()
      print("returning Singleton")
      return Logger.__instance
   def __init__(self):
      """ Virtually private constructor. """
      if Logger.__instance != None:
         raise Exception("This class is a singleton!")
      else:
        print("initializing Logger")
        Logger.__instance = Meta_Logger ()
		

if __name__ == '__main__':
	
	my_logger=Logger()
	# print("You're using {}".format(my_logger.platform))
	my_logger.log()

	