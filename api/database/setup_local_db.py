# creates the DynamoDB table locally
# only need to create the table once

import boto3, os
from dotenv import load_dotenv
load_dotenv()

def get_dynamodb():
    return boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'local'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'local'),
    )

def create_table():
    dynamodb = get_dynamodb()
    try:
        table = dynamodb.create_table(
            TableName=os.getenv('DYNAMODB_TABLE', 'dog-shelter-tamagochi-ai_players'),
            KeySchema=[
                {'AttributeName': 'player_name', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'player_name', 'AttributeType': 'S'},
            ],
            BillingMode='PAY_PER_REQUEST', #PAY_PER_REQUEST (on-demand) bc no capacity planning (guessing traffic levels) needed, scales automatically, free tier covers portfolio traffic
        )
        table.wait_until_exists()
        print(f"Table created: {table.table_name}")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("Table already exists — skipping")

if __name__ == '__main__':
    create_table()