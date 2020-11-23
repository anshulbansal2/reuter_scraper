import sys

sys.path.insert(0, '/reuter_scraper')
from config import *
from utils.sqs_utils import *
logger = Logger(logger='isin_producer')
from data import data


# Create SQS client
sqs = SQSClient('http://localhost:9324', 'us-east-1')

queue_url = QueueUrl[ENV]['url'] if ENV == 'local' else sqs.queue_url(QueueUrl[ENV]['queue_name'],
                                                                      QueueUrl[ENV]['aws_account_id'])


if __name__ == "__main__":
	isin_counter = 0
	for value in data:
		isin_counter += 1
		logger.info("{} producing isin: {} to queue: {}".format(isin_counter,str(value), queue_url),
		            bucket=REAUTER_SCRAPER.ISIN_producer)
		sqs.produce_messages(queue_url, str(value))
