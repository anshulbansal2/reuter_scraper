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

REUTERS_API = {
    
    'Recommendations' : {
        'url': 'https://apac1.apps.cp.thomsonreuters.com/Apps/RecommendationTPApp/1'
                           '.10.8/GetEstimateDetails',
        
        'post_data' : """%s|true""",
        
        'dynamodb_table' : 'stock_recomm_data'
    },
    
    'Pricehistory': {
        'url': 'https://apac1.apps.cp.thomsonreuters.com/TA/TAService.svc/json2'
                     '/CalculateAllData',
        
        'post_data': """{"messages":[{"RequestInfos":[{
	    "__type":"TSRequest:http://www.thomsonreuters.com/ns/2012/01/01/webservices/TAService_1/",
	    "RIC": "%s", "Interval":4, "TradePeriod":"1", "ColumnMask":31, "TimeZone":"",
	    "IntervalMultiplier":1, "RemoveGaps":true, "DateRange":3, "DateRangeMultiplier":5,
	    "AdjustInterval":true}]}]}""",
        
        'dynamodb_table' : 'stock_pricing_history'
    }
}

QueueUrl= {
    'local' : {
        'url': 'http://localhost:9324/queue/test'
    },
    'prod': {
     'queue_name': '',
     'aws_account_id': ''
    }
    
}
