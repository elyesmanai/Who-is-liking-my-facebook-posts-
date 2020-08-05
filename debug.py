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

# Global Variables
driver = None

old_height = 0

urls=[]
comment_threads=[]

#reacters=()
#commenters=()
reacters=[]
commenters=[]
facebook="mbasic.facebook.com"

posts=[]

def check_height():
	new_height = driver.execute_script("return document.body.scrollHeight")
	return new_height != old_height

		

def safe_find_element_by_id(driver, elem_id):
	try:
		return driver.find_element_by_id(elem_id)
	except NoSuchElementException:
		return None

def login(email, password):
	""" Logging into our own profile """

	try:
		global driver

		options = Options()

		#  Code to disable notifications pop up of Chrome Browser
		options.add_argument("--disable-notifications")
		options.add_argument("--disable-infobars")
		options.add_argument("--mute-audio")
		# options.add_argument("headless")

		try:
			platform_ = platform.system().lower()
			if platform_ in ['linux', 'darwin']:
				print ("bazinga")
				driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
			else:
				driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
			driver.header_overrides ={'Accept-Language': 'en-US,en;q=0.8'}
		except:
			print("Kindly replace the Chrome Web Driver with the latest one from "
				  "http://chromedriver.chromium.org/downloads "
				  "and also make sure you have the latest Chrome Browser version."
				  "\nYour OS: {}".format(platform_)
				  )
			exit()

		driver.get("https://mbasic.facebook.com")
		driver.maximize_window()

		# filling the form
		driver.find_element_by_name('email').send_keys(email)
		driver.find_element_by_name('pass').send_keys(password)

		# clicking on login button
		driver.find_element_by_name("login").click()

		# if your account uses multi factor authentication
		mfa_code_input = safe_find_element_by_id(driver, 'approvals_code')

		if mfa_code_input is None:
			return

		mfa_code_input.send_keys(input("Enter MFA code: "))
		driver.find_element_by_id('checkpointSubmitButton').click()

		# there are so many screens asking you to verify things. Just skip them all
		while safe_find_element_by_id(driver, 'checkpointSubmitButton') is not None:
			dont_save_browser_radio = safe_find_element_by_id(driver, 'u_0_3')
			if dont_save_browser_radio is not None:
				dont_save_browser_radio.click()

			driver.find_element_by_id('checkpointSubmitButton').click()

	except Exception as e:
		print("There's some error in log in.")
		print(sys.exc_info()[0])
		exit()
def append_urls():
	global urls
	posts=driver.find_elements_by_xpath("//*[contains(text(), 'Actualité intégrale')]")
	#print(posts)
	for post in posts :
		url=post.get_attribute('href')
		urls.append(url)
def save_urls():
	global urls
	with open("urls.p",'wb') as pickle_file:
		pickle.dump(urls,pickle_file)
		pickle_file.close()
def load_urls():
	urls=[]
	with open("urls.p",'rb') as pickle_file:
		urls=pickle.load(pickle_file)
		#print (urls[0])
		pickle_file.close()
		return urls



def get_urls_and_save():
	global driver
	driver.get('https://mbasic.facebook.com/manai.elyes')
	
	#loads new page
	no_exception=True
	#for i in range (0,3):
	while (no_exception):
		try:
			next_page=driver.find_element_by_xpath("//*[contains(text(), 'Afficher plus d’actualités')]")
			append_urls()
			next_page.click()
		except Exception as e :
			print(e)
			print("You've just scrapped all content ! bazinga !")
			no_exception=False
			#pickle.dump(urls, open())		
	save_urls()


def get_post_date():
	global driver 
	date=driver.find_element_by_xpath("//abbr") 
	print(date.text)
	return date.text


# gives back the list of the nested urls so we can iterate on them after
def manage_nested_comments():
	print('_________')
	print(comment_threads)
	print('_________')
	for comment_thread in comment_threads:
		print("href is ")
		print(comment_thread.get_attribute('href'))
		comment_thread.click()
		get_users_in_comments_page()

# quick fix : comment threads should be global	
def get_nested_comments():
	global driver 
	comment_thread_container=driver.find_element_by_xpath("//div[contains(@id, 'comment_replies_more_1')]")
	print(comment_thread_container.text)
	comment_thread=comment_thread_container.find_element_by_tag_name("a")
	print(comment_thread.get_attribute('href'))
	comment_threads.append(comment_thread)
	print(comment_threads)


# modify this 
def get_users_in_comments_page():
	global driver 
	global commenters
	users=driver.find_elements_by_xpath("//h3")
	for user in users:
		print(user.text)
		commenters.append(user.text)
#change to english 
def navigate_comments():
	global driver
	print('navigating')
	try :
		#driver.implicitly_wait(2)
		next_page=driver.find_element_by_xpath("//*[contains(text(), 'Commentaires précédents')]")
	except Exception as e :
		print(e)
	print('next page')
	print(next_page.get_attribute('href'))
	next_page.click()

def get_commenters():
	global commenters
	try :
		while True :
			get_users_in_comments_page()
			#driver.implicitly_wait(3)
			#get_nested_comments()
			navigate_comments()
	except :
		print('no more comments here !')
		print(commenters)
	#manage_nested_comments()


def get_users_in_react_page():
	global driver 
	global reacters
	users=driver.find_elements_by_class_name('bj')
	for user in users:
		print(user.text)
		reacters.append(user.text)

#change to english 
def navigate_reacts():
	global driver
	next_page=driver.find_element_by_xpath("//*[contains(text(), 'En afficher davantage')]")
	next_page.click()


def get_reacters () :
	global driver
	global reacters
	try :
		print('======================================')
		reacts_link=driver.find_element_by_xpath("//a[contains(@href,'/ufi/reaction')]")
		reacts_link.click()
		try :
			while (True):
				get_users_in_react_page()
				navigate_reacts()
		except :
			print(reacters)
			print('bazinga ! there it is ! all your user reacts')
	except Exception as e :
		print(e)
		print("this post doesn't have reacts")
	
def create_post_dictionary():
	global commenters
	global reacters
	global posts
	post={}

	post['date']=get_post_date()
	post['commenters']=commenters
	post['reacters']=reacters
	print (post)
	posts.append(post)

def init_driver_url(url):
	global driver
	driver.get(url)

def get_post_info(url):
	init_driver_url(url)
	get_post_date()
	init_driver_url(url)
	get_reacters()
	init_driver_url(url)
	get_commenters()
	create_post_dictionary()
	
def save_posts_to_json():
	with open("posts.json", "w") as json_file:
		json.dump(posts, json_file)


if __name__ == '__main__':
	
	email = "blablatest" # your fb mail
	password = "blablatest" # your fb pass
	#print("\nStarting Scraping...")
	login(email, password)
	
	#gets the page
	#driver.get('https://mbasic.facebook.com/manai.elyes')
	#saves all urls
	#get_urls_and_save()

	#load saved urls
	#urls=load_urls()
	#print(len(urls))
	
	#for(url in urls)
	#for i in range (0,1):
	#	get_post_info(urls[i])
	#print(posts)
	#save_posts_to_json()