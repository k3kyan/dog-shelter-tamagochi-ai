# DynamoDB logic
# modular separation - keep database logic outside of endpoints, easier to swap dynamodb for something else later if needed

import boto3, os
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from decimal import Decimal
load_dotenv()

# dynamodb connection
def get_table():
    """Returns the DynamoDB table resource."""
    endpoint = os.getenv('DYNAMODB_ENDPOINT')
    kwargs = {'region_name': os.getenv('AWS_DEFAULT_REGION', 'us-east-1')}
    # if running locally, add these 3 keys. Otherwise, on real AWS, boto3 falls back to IAM role auth
    if endpoint:
        # local dev — point boto3 at DynamoDB Local container
        kwargs['endpoint_url'] = endpoint
        kwargs['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID', 'local')
        kwargs['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
    # no endpoint = real AWS = boto3 uses the Lambda IAM role automatically
    dynamodb = boto3.resource('dynamodb', **kwargs) #remember, ** unpacks dicts
    return dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'dog-shelter-tamagochi-ai-players'))

# TODO: Note for now, get_table() is called on each db operation rather than once at module level
# BECAUSE
# easier to swap endpoint_url between LOCAL and AWS
# SO IN FUTURE, MAYBE WILL CHANGE THIS ONCE I DEPLOY THIS APP TO AWS
