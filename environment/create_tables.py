import boto3
from config import ACCESS_KEY, SECRET_ACCESS_KEY, REGION

# Create DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION
)

def create_signup_table():
    table = dynamodb.create_table(
        TableName='signup_db',
        KeySchema=[
            {
                'AttributeName': 'email',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    
    return table

# Call the create_signup_table function
create_signup_table()
