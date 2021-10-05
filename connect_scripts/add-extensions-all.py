import boto3
import json
from boto3.dynamodb.conditions import Key,Attr

# TODO:function to check if agent has an extension, function to assign extension, and check function for exception handling and readability
 
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1') 
table = dynamodb.Table('AgentData')

connect = boto3.client('connect')

global unused = []

# checks if a user is currently assigned an extension 
def has_extension(username):
    u = username

    response = table.query(
            IndexName='byAgent',
            KeyConditionExpression=Key('AgentLoginName').eq(u))
    hasExt = response.get('Items', {})

    if (bool(hasExt)):
        return False 
    else:
        return True 
        
# gets list of connect users, returns as list
def  get_users():
    users = []
    iid ='794790f5-0ae2-4348-806a-f58bf245ab3f'
    response = connect.list_users(
    InstanceId=iid,
    MaxResults=10
    )

    while "NextToken" in response:
        addUsers = response.get('UserSummaryList')

        users.append(addUsers)

        response = connect.list_users(
                NextToken=response["NextToken"],
                InstanceId=iid,
                MaxResults=10)

    users.append(response.get('UserSummaryList'))
    return users

# gets unused extensions 100 at a time
def get_unused_ext():
    global unused

    response = table.query(
    IndexName='skIndex',
    Limit=100,
    KeyConditionExpression=Key('sk').eq("nu"))
    
    
    unused = response.get('Items')

    return 
#TODO: finish
def set_extension(username):
    u = username
    global unused

    if not bool(unused):
        get_unused_ext()


def main():

if __name__ == "__main__":
    main()


