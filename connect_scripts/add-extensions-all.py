import boto3
import json
# TODO:function to check if agent has an extension, function to assign extension, and get_response function for exception handling and readability

conClient = boto3.client('connect')
users = []
iid ='794790f5-0ae2-4348-806a-f58bf245ab3f'

response = conClient.list_users(
InstanceId=iid,
MaxResults=10
)

while "NextToken" in response:
    addUsers = response.get('UserSummaryList')

    users.append(addUsers)
    #print(response.get('UserSummaryList'))
    response = conClient.list_users(
            NextToken=response["NextToken"],
            InstanceId=iid,
            MaxResults=10)

users.append(response.get('UserSummaryList'))
print(type(users))
print(users)

