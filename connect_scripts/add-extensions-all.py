import boto3
import json
from boto3.dynamodb.conditions import Key,Attr
# TODO:function to check if agent has an extension, function to assign extension, and check function for exception handling and readability
 
# queries global secondary index for agent, if found returns true
global unused = []

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
def get_unused_ext():

    response = table.query(
    IndexName='skIndex',
    Limit=100,
    KeyConditionExpression=Key('sk').eq("nu"))
    
    
    unused = response.get('Items')

    return unused

def set_extension(username):
    u = username
    dbClient = boto3.resource('dynamodb')
    table = dbClient.Table('AgenttoAgent')

    if not bool(unused):
        get_unused_ext()


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

