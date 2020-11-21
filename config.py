import os
import os.path
from datetime import timedelta

# ENV = "prod" #local
ENV = os.environ['ENV']

# DYNAMO DB CONFIGS
DYNAMO_CONFIGS = {
    'prod': {
        'region_name': 'ap-south-1',
        'endpoint_url': 'https://dynamodb.ap-south-1.amazonaws.com'
    },
    'local': {
        'region_name': 'us-west-2',
        'endpoint_url': 'http://localhost:8000'
    }
}

DYNAMO_TABLES = {
    'reuter_stock_data': 'reuter_stock_data'
}

REUTERS_API = {
    'GetEstimateDetails' : 'https://apac1.apps.cp.thomsonreuters.com/Apps/RecommendationTPApp/1.10.8/GetEstimateDetails'
}


QueueUrl= {
    'local' : {
        'url': 'http://localhost:9324/queue/default'
    },
    'prod': {
     'queue_name': '',
     'aws_account_id': ''
    }
    
}
