import boto3
import json

conClient = boto3.client('connect')

response = conClient.list_users(
InstanceId='794790f5-0ae2-4348-806a-f58bf245ab3f',
MaxResults=10
)
users = response.get('UserSummaryList')
print(type(users))
print(users)
