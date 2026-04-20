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
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local'),
    )
    return dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'dog-shelter-tamagochi-ai_players'))

# TODO: Note for now, get_table() is called on each db operation rather than once at module level
# BECAUSE
# easier to swap endpoint_url between LOCAL and AWS
# SO IN FUTURE, MAYBE WILL CHANGE THIS ONCE I DEPLOY THIS APP TO AWS
# ACTUALLY
# maybe ill do same thing as my website and make it into an env var switch at the start. will do this later. 
