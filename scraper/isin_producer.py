import sys

sys.path.insert(0, '/reuter_scraper')
from config import *
from utils.sqs_utils import *
logger = Logger(logger='isin_producer')



def fetch_ISIN():
	dirname = os.path.dirname(__file__)
	file_name = os.path.join(dirname, '../ISIN.txt')
	# file_name = os.path('./ISIN.txt')
	return [line.rstrip('\n') for line in open(file_name)]

# Create SQS client
sqs = SQSClient('http://localhost:9324', 'us-east-1')

queue_url = QueueUrl[ENV]['url'] if ENV == 'local' else sqs.queue_url(QueueUrl[ENV]['queue_name'],
                                                                      QueueUrl[ENV]['aws_account_id'])

if __name__ == "__main__":
	isin_list = fetch_ISIN()
	isin_counter = 0
	for isin in isin_list:
		isin_counter += 1
		logger.info("{} producing isin: {} to queue: {}".format(isin_counter,isin, queue_url),
		            bucket=REAUTER_SCRAPER.ISIN_producer)
		sqs.produce_messages(queue_url, isin)
