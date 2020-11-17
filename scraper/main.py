import sys
import os
sys.path.insert(0, '/reuter_scraper')
import time
import datetime
import traceback
import requests
from decimal import Decimal
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from logger.logger import Logger
from logger.log_bucket import *
from config import *
from utils.util import *
from utils.dynamo_utils import *

logger = Logger(logger='ReuterScraper')

reuter_stock_data_table = get_dynamo_resource(DYNAMO_TABLES['reuter_stock_data'])

def get_logged_in_driver(user_id, pwd):
	
	# Get chrome web driver
	options = Options()
	options.add_argument("--headless")
	options.add_argument("window-size=1400,1500")
	options.add_argument("--disable-gpu")
	options.add_argument("--no-sandbox")
	options.add_argument("start-maximized")
	options.add_argument("enable-automation")
	options.add_argument("--disable-infobars")
	options.add_argument("--disable-dev-shm-usage")
	
	driver = webdriver.Chrome(options=options)

	try:
			
		driver.get("https://apac1.apps.cp.thomsonreuters.com")
		userid = driver.find_element_by_name("IDToken1")
		password = driver.find_element_by_name("IDToken2")
		userid.send_keys(user_id)
		password.send_keys(pwd)
		signin = driver.find_element_by_id("AAA-AS-SI1-SE014")
		signin.submit()
	
		main = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.ID, "AAA-AS-SI2-SE004"))
		)
	
		# if already logged in somewhere else, logout from there and login again
		if "already signed" in main.text:
			logger.info("User {} is already signed in elsewhere, expiring all other "
			                    "sessions and login again".format(user_id),
			            bucket=REAUTER_SCRAPER.reuter_login)
		
			driver.find_element_by_id("AAA-AS-SI2-SE009").click()
		
		# wait for 10 sec before confirming logged in page title
		time.sleep(20)
	
		if driver.title == 'Sample Layout - Market Monitoring':
			logger.info("Login successful for user {}".format(user_id),
			            bucket=REAUTER_SCRAPER.reuter_login)
		
	except Exception as e:
		tback = str(traceback.format_exc().splitlines())
		ex_detail = {}
		ex_detail['traceback'] = tback
		ex_detail['ExceptionMessage'] = str(e)
		logger.error("Login failed for user {} with exception: {}".format(user_id,
		str(ex_detail)), bucket=REAUTER_SCRAPER.reuter_login)
		driver.quit()
			
	return driver

	
def fetch_ISIN():
	dirname = os.path.dirname(__file__)
	file_name = os.path.join(dirname, '../ISIN.txt')
	return [line.rstrip('\n') for line in open(file_name)]

	
def fetch_recommendation_estimates(api_cookies, data):
	try:
		url = REUTERS_API['GetEstimateDetails']
		res = requests.post(url, cookies=api_cookies, data=data)
		if res.status_code == 200:
			logger.info(message="Fetch successful for {}".format(data),
			            bucket=REAUTER_SCRAPER.recommendation_estimates,
			            stage='Estimates API Calling')
			return json.loads(res.text, parse_float=Decimal)
			
	except Exception as e:
		error = {}
		error['ExceptionMessage'] = str(e)
		error['trace'] = traceback.format_exc().splitlines()
		logger.error(message="Failed to fetch recommendation estimates for {}".format(
			str(data)),
			bucket=REAUTER_SCRAPER.recommendation_estimates,
			stage='Estimates API Calling',
			extra_message=str(error))


def save_recommendation_estimates(api_cookies, isin_list):
	
	with reuter_stock_data_table.batch_writer(overwrite_by_pkeys=['isin', 'created_at']) as batch:
		for data in isin_list:
			logger.info(message="fetch and save for ISIN: {}".format(data),
			            bucket=REAUTER_SCRAPER.recommendation_estimates,
			            stage='Dynamo save estimates')
			
			estimate_json = fetch_recommendation_estimates(api_cookies, data+'|true')
			ct = int(time.time())
			estimate_json['isin'] = data
			estimate_json['created_at'] = ct
			logger.debug("etimate json: {}".format(estimate_json),
			             bucket=REAUTER_SCRAPER.recommendation_estimates,
			             stage='Dynamo save estimates')
			batch.put_item(Item=remove_empty_from_dict(estimate_json))
	

if __name__ == '__main__':
	userid = sys.argv[1]
	password = sys.argv[2]
	
	# Get loggedIn driver
	logged_in_driver = get_logged_in_driver(userid, password)
	
	# Get loggedIn cookies
	driver_cookies = logged_in_driver.get_cookies()
	request_cookies = {c['name']: c['value'] for c in driver_cookies}
	logger.info("request_cookies: {}".format(str(request_cookies)), bucket=REAUTER_SCRAPER.master)
	
	isin_list = fetch_ISIN()
	
	for chunk in get_chunks(isin_list, 500):
		save_recommendation_estimates(request_cookies, chunk)
