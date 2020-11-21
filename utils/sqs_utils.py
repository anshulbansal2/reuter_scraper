import sys
sys.path.insert(0, '/reuter_scraper')
import boto3
from config import *
import traceback
from logger.log_bucket import *
from logger.logger import Logger
logger = Logger(logger='sqs_util')


if ENV == "local":
	os.environ["AWS_ACCESS_KEY_ID"] = "test"
	os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


class SQSClient:
	
	def __init__(self, endpoint_url, region='us-east-1'):
		# Initialise Boto3 Session
		session = boto3.session.Session()
		
		# # Initialise SQS client
		if ENV == 'local':
			self.sqs = session.client('sqs', endpoint_url=endpoint_url, region_name=region)
		else:
			self.sqs = session.client('sqs')
			
		print("SQSClient Initialised")

	def consume_messages(self, queue_url):
		res = self.sqs.receive_message(QueueUrl=queue_url, AttributeNames=[""],
			MaxNumberOfMessages=1,
			MessageAttributeNames=[
				'All'
			],
			VisibilityTimeout=0,
			WaitTimeSeconds=0)
		return res
	
	def consume_next_message(self, queue_url):
		""" Receive Message from Queue """
		response = self.sqs.receive_message(
			QueueUrl=queue_url,
			AttributeNames=[""],
			MaxNumberOfMessages=1,
			MessageAttributeNames=[
				'All'
			],
			VisibilityTimeout=0,
			WaitTimeSeconds=10,  # FIXME This timeout needs some more thought!!!
		)
		print(response)
		message = response['Messages'][0]  # we only want the first message.
		print("Message -> %s" % message)
		return message

	def produce_messages(self, queue_url, message):
		response = self.sqs.send_message(
			QueueUrl=queue_url,
			MessageBody=(message)
		)
		msg_id = response['MessageId']
		logger.info("message produced successfully with Message ID -> %s" % msg_id)


	def create_queue(self, name):
		""" Create Queue in SQS, returning the QueueURL """
		response = self.sqs.create_queue(
			QueueName=name,
			Attributes={
				'DelaySeconds': '60',
				'MessageRetentionPeriod': '86400'
			}
		)
		logger.info("QueueCreated -> %s" % response)
		queue_url = response['QueueUrl']
		return queue_url

	def delete_queue(self, queue_url):
		""" Delete the queue, given the following URL """
		response = self.sqs.delete_queue(QueueUrl=queue_url)
		logger.info("Deleted Queue -> %s" % queue_url)
		return ("Queue at URL {0} deleted").format(queue_url)

	def delete_message(self, queue_url, receipt_handle):
		""" delete Message from Queue given receipt_handle """
		try:
			self.sqs.delete_message(
				QueueUrl=queue_url,
				ReceiptHandle=receipt_handle
			)
			logger.info(message="deleted message from sqs queue: {}".format(
				queue_url),
				bucket=REAUTER_SCRAPER.recommendation_estimates,
				stage='dynamo_save_estimates')
		except Exception as e:
			error = {}
			error['ExceptionMessage'] = str(e)
			error['trace'] = traceback.format_exc().splitlines()
			logger.error(message="Failed to delete message for queue: {}".format(
				str(queue_url)),
				bucket=REAUTER_SCRAPER.recommendation_estimates,
				stage='sql_delete_message',
				extra_message=str(error))
			raise
		
	def queue_url(self, queue_name, acc_id):
		return self.sqs.get_queue_url(queue_name, acc_id)

