import sys

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
from utils.sqs_utils import *
from utils.dynamo_utils import *
from signal import SIGINT, SIGTERM, signal
import boto3
logger = Logger(logger='ReuterScraper')

sqs = SQSClient('http://localhost:9324', 'us-east-1')

# queue = sqs.get_queue_by_name(QueueName=os.environ["default"])
reuter_stock_data_table = get_dynamo_resource(DYNAMO_TABLES['reuter_stock_data'])

queue_url = QueueUrl[ENV]['url'] if ENV == 'local' else sqs.queue_url(QueueUrl[ENV]['queue_name'],
                                                                      QueueUrl[ENV]['aws_account_id'])

# isin_counter = 0
userid = ''
password = ''


def get_logged_in_cookies(user_id, pwd):
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
		
		# Get loggedIn cookies
		driver_cookies = driver.get_cookies()
		request_cookies = {c['name']: c['value'] for c in driver_cookies}
		logger.info("request_cookies: {}".format(str(request_cookies)),
		            bucket=REAUTER_SCRAPER.master)
		driver.quit()
		
		return request_cookies
	
	except Exception as e:
		tback = str(traceback.format_exc().splitlines())
		ex_detail = {}
		ex_detail['traceback'] = tback
		ex_detail['ExceptionMessage'] = str(e)
		logger.error("Login failed for user {} with exception: {}".format(user_id,
		                                                                  str(ex_detail)),
		             bucket=REAUTER_SCRAPER.reuter_login)
		driver.quit()


def fetch_recommendation_estimates(api_cookies, data):
	url = REUTERS_API['GetEstimateDetails']
	res = requests.post(url, cookies=api_cookies, data=data)
	return res


def fetch_and_save_estimates(api_cookies, data):
	logger.info(message="fetch and save estimates for ISIN: {}".format(data),
	            bucket=REAUTER_SCRAPER.recommendation_estimates,
	            stage='dynamo_save_estimates')
	
	res = fetch_recommendation_estimates(api_cookies, data + '|true')
	
	if res.status_code == 200:
		estimate_json = json.loads(res.text, parse_float=Decimal)
		if estimate_json and isinstance(estimate_json, dict):
			ct = int(time.time())
			estimate_json['isin'] = data
			estimate_json['created_at'] = ct
			logger.debug("etimate json: {}".format(str(estimate_json)),
			             bucket=REAUTER_SCRAPER.recommendation_estimates,
			             stage='dynamo_save_estimates')
			reuter_stock_data_table.put_item(Item=remove_empty_from_dict(estimate_json))
			
			logger.info(
				message="Successfully saved estimates for ISIN: {}".format(data),
				bucket=REAUTER_SCRAPER.recommendation_estimates,
				stage='dynamo_save_estimates')
		else:
			logger.error(message="API with status code 200 returned error json: {} for "
			                     "isin : {}".format(estimate_json, data),
			             bucket=REAUTER_SCRAPER.recommendation_estimates,
			             stage='estimates_api_calling')
	
	else:
		error_message = {}
		error_message['status'] = res.status_code
		error_message['error_reason'] = res.reason
		logger.error(message=" fetch API call failed for isin : {}".format(
			data), bucket=REAUTER_SCRAPER.recommendation_estimates,
			stage='estimates_api_calling',
			extra_message=str(error_message))
		
		logger.info("session expired, getting loggedIn cookies again")
		request_cookies = get_logged_in_cookies(userid, password)
		
		fetch_and_save_estimates(request_cookies, data)


class SignalHandler:
	def __init__(self):
		self.received_signal = False
		signal(SIGINT, self._signal_handler)
		signal(SIGTERM, self._signal_handler)
	
	def _signal_handler(self, signal, frame):
		print(f"handling signal {signal}, exiting gracefully")
		self.received_signal = True


if __name__ == "__main__":
	userid = sys.argv[1]
	password = sys.argv[2]
	request_cookies = get_logged_in_cookies(userid, password)
	logger.info(message="Consuming messages from sqs queue: {}".format(queue_url),
	            bucket=REAUTER_SCRAPER.recommendation_estimates,
	            stage='sqs_consumer')
	signal_handler = SignalHandler()
	while not signal_handler.received_signal:
		res = sqs.consume_messages(queue_url)
		if 'Messages' in res.keys():
			for message in res['Messages']:
				isin = message['Body']
				try:
					fetch_and_save_estimates(request_cookies, isin)
				except Exception as e:
					error = {}
					error['ExceptionMessage'] = str(e)
					error['trace'] = traceback.format_exc().splitlines()
					logger.error(message="Failed to save recommendation estimate json for {}".format(
						isin),
						bucket=REAUTER_SCRAPER.recommendation_estimates,
						stage='dynamo_save_estimates',
						extra_message=str(error))
					raise
					
				receipt_handle = message['ReceiptHandle']
				
				# Delete received message from queue
				sqs.delete_message(queue_url, receipt_handle)

