from boto3 import resource
from config import *

from logger.logger import Logger
logger = Logger(logger='raw')


def get_dynamo_resource(table_name):
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
    table = dynamodb_resource.Table(table_name)
    return table


def get_items_by_partition_key(hash_key, hash_value, table_name=None, table=None,
                               attribute_list=None):
    items = []
    try:
        if not table:
            table = get_dynamo_resource(DYNAMO_TABLES[table_name])

        if attribute_list:
            response = table.query(KeyConditionExpression=Key(hash_key).eq(str(hash_value)),
                                   ProjectionExpression=str(",".join(attribute_list)),
                                   Select="SPECIFIC_ATTRIBUTES", ConsistentRead=True)

        else:
            response = table.query(KeyConditionExpression=Key(hash_key).eq(hash_value),
                                   ConsistentRead=True)
        items = response.get('Items', [])
        return items
    except Exception:
        logger.error(message="Unable to get items from dynamo table {}, for partition key: {},"
                             " and value: {}".format(table_name, hash_key, hash_value))
    return items


def get_item_by_primary_key(partition_key, partition_value,
                            sort_key, sort_value,
                            table_name=None, table=None):
    item = None
    try:
        if not table:
            table = get_dynamo_resource(DYNAMO_TABLES[table_name])
        response = table.get_item(
            Key={
                partition_key: partition_value,
                sort_key: sort_value
            }
        )
        item = response.get('Item')
    except Exception:
        logger.error(message="Unable to get item from dynamo table {}, for partition key: {},"
                             ", value: {}, sort_key: {} and sort_value: {}".format(table_name,
                                                                                   partition_key,
                                                                                   partition_value,
                                                                                   sort_key,
                                                                                   sort_value))
    return item


def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and
                    remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d


# Get a item by partition key and sort key
def get_item_by_keys(partition_key, partition_key_value, sort_key,
                     sort_key_value, table_name = None, table = None):
    try:
        if not table:
            table = get_dynamo_resource(DYNAMO_TABLES[table_name])
        item = table.get_item(
            Key = {
                partition_key : partition_key_value,
                sort_key : sort_key_value
            }
        )
        return item['Item']
    except Exception:
        logger.error(message="Unable to get item from dynamo table :{},partition key :{}"
                             "partition key value : {}, sort key  : {} , sort key value : {}"
                             .format(
                                 table_name,
                                 partition_key,
                                 partition_key_value,
                                 sort_key,
                                 sort_key_value
                             )
        )
        return None


# Removes a item by partition key and sort key
def remove_item_by_keys(partition_key, partition_key_value, sort_key,
                        sort_key_value, table_name = None, table = None):
    try:
        if not table:
            table = get_dynamo_resource(DYNAMO_TABLES[table_name])
        table.delete_item(
            Key = {
                partition_key : partition_key_value,
                sort_key : sort_key_value
            }
        )
        return True
    except Exception:
        logger.error(message="Unable to delete item from dynamo table :{},partition key :{}"
                             "partition key value : {}, sort key  : {} , sort key value : {}"
                             .format(
                                 table_name,
                                 partition_key,
                                 partition_key_value,
                                 sort_key,
                                 sort_key_value
                             )
        )
        return False
    
    
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
		TableName="reuter_stock_data",
		KeySchema=[
			{
				'AttributeName': 'isin',
				'KeyType': 'HASH'  # Partition key
			},
			{
				'AttributeName': 'created_at',
				'KeyType': 'RANGE'  # Sort key
			}
		],
		AttributeDefinitions=[
			{
				'AttributeName': 'isin',
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
