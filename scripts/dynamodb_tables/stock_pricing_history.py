from boto3 import resource
from config import *


def create_table():
	region_name = DYNAMO_CONFIGS[ENV]['region_name']
	endpoint_url = DYNAMO_CONFIGS[ENV]['endpoint_url']
	
	if ENV == 'prod':
		dynamodb_resource = resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
	else:
		dynamodb_resource = resource('dynamodb',
		                             region_name=region_name,
		                             endpoint_url=endpoint_url,
		                             aws_access_key_id='dummy_access_key',
		                             aws_secret_access_key='dummy_secret_key',
		                             verify=False)
	table = dynamodb_resource.create_table(
		TableName="stock_pricing_history",
		KeySchema=[
			{
				'AttributeName': 'id',
				'KeyType': 'HASH'  # Partition key
			},
			{
				'AttributeName': 'created_at',
				'KeyType': 'RANGE'  # Sort key
			}
		],
		AttributeDefinitions=[
			{
				'AttributeName': 'id',
				'AttributeType': 'S'
			},
			{
				'AttributeName': 'created_at',
				'AttributeType': 'N'
			},
		],
		BillingMode='PAY_PER_REQUEST'
	)
	print("Table status:", table.table_status)