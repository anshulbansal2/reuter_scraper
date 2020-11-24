import sys

sys.path.insert(0, '/reuter_scraper')
from config import *
from utils.sqs_utils import *
logger = Logger(logger='reuters_sqs_producer')
from data import data


# Create SQS client
sqs = SQSClient(SQS_CONFIGS[ENV]['endpoint_url'], SQS_CONFIGS[ENV]['region_name'])
queue_url = SQS_CONFIGS[ENV]['queueurl']


if __name__ == "__main__":
	isin_counter = 0
	for value in data:
		isin_counter += 1
		logger.info("{} producing data: {} to queue: {}".format(isin_counter,str(value),
		                                                         queue_url),
		            bucket=REAUTER_SCRAPER.ISIN_producer)
		sqs.produce_messages(queue_url, str(value))
