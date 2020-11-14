import sys
import os
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
logger = logging.getLogger('ReuterScraper')


def get_logged_in_driver(user_id, pwd):
	
	# Get chrome web driver
	dirname = os.path.dirname(__file__)
	driver_path = os.path.join(dirname, '../chromedriver')
	print("driver_path: "+driver_path)
	driver = webdriver.Chrome(driver_path)
	
	try:
			
		driver.get("https://apac1.apps.cp.thomsonreuters.com")
		userid = driver.find_element_by_name("IDToken1")
		password = driver.find_element_by_name("IDToken2")
		userid.send_keys(user_id)
		password.send_keys(pwd)
		signin = driver.find_element_by_id("AAA-AS-SI1-SE014")
		signin.submit()
		
		main = WebDriverWait(driver, 5).until(
			EC.presence_of_element_located((By.ID, "AAA-AS-SI2-SE004"))
		)
			
		# if already logged in somewhere else, logout from there and login again
		if "already signed" in main.text:
			print("User {} is already signed in elsewhere, expiring all other "
			                    "sessions and login again".format(user_id))
			
			driver.find_element_by_id("AAA-AS-SI2-SE009").click()
			
		# wait for 10 sec before confirming logged in page title
		time.sleep(10)
			
		if driver.title == 'Sample Layout - Market Monitoring':
			print("Login successful for user {}".format(user_id))
		
	except Exception as e:
		tback = str(traceback.format_exc().splitlines())
		ex_detail = {}
		ex_detail['traceback'] = tback
		ex_detail['ExceptionMessage'] = str(e)
		logger.error("Login failed for user {} with exception: {}".format(user_id,
		ex_detail))
		driver.quit()
			
	return driver

	
def fetch_ISIN():
	file_name = '/Users/mmt6293/PycharmProjects/reuter_scraper/ISIN.txt'
	return [line.rstrip('\n') for line in open(file_name)]

	
def get_recommendation_estimates(api_cookies, data):
		
		recom_url = 'https://apac1.apps.cp.thomsonreuters.com/Apps/RecommendationTPApp/1.10.8/GetEstimateDetails'
		res = requests.post(recom_url, cookies=api_cookies, data=data)
		if res.status_code == 200:
			print("recommendation json: {}".format(res.text))


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	userid = sys.argv[1]
	password = sys.argv[2]
	
	print("\n\n"+userid+"\n\n"+password)
	.gitignore
	# Get loggedIn driver
	logged_in_driver = get_logged_in_driver(userid, password)
	
	# Get loggedIn cookies
	driver_cookies = logged_in_driver.get_cookies()
	request_cookies = {c['name']: c['value'] for c in driver_cookies}
	print("request_cookies: {}".format(str(request_cookies)))
	
	for isin in fetch_ISIN():
		print("\n\n Fetching recommendation for isin: {}".format(isin))
		get_recommendation_estimates(request_cookies, isin+'|true')
	

