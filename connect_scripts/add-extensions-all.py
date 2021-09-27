import boto3
import json
from boto3.dynamodb.conditions import Key,Attr
# TODO:function to check if agent has an extension, function to assign extension, and check function for exception handling and readability
 
# queries global secondary index for agent, if found returns true
def has_extension(username):
    u = username
    dbClient = boto3.resource('dynamodb')
    table = dbClient.Table('AgenttoAgent')
    response = table.query(
            IndexName='byAgent',
            KeyConditionExpression=Key('AgentLoginName').eq(u))
    hasExt = response.get('Items', {})

    if (hasExt == []):
        return False 

    else:
        return True 

def set_extension(username):
    u = username
    dbClient = boto3.resource('dynamodb')
    table = dbClient.Table('AgenttoAgent')
    
    response1 = table.scan(
    #TODO:scan parameters for available extensions
    )
    availExt = response1.get('Items', {})
    
    print (availExt)


    print(response1)
def main():

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

        response = conClient.list_users(
                NextToken=response["NextToken"],
                InstanceId=iid,
                MaxResults=10)

    users.append(response.get('UserSummaryList'))
    set_extension('bbob') 
    

if __name__ == "__main__":
    main()

