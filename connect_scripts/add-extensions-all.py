import boto3
import json
from boto3.dynamodb.conditions import Key,Attr

# TODO: function to remove user, exception handling, event handler for lambda
# , backoff algorithm for connect api request in get_users, remove users
# not used
 
dynamodb = boto3.client('dynamodb', region_name = 'us-east-1') 
res_dynamodb = boto3.resource('dynamodb')
table = res_dynamodb.Table('AgentData')

connect = boto3.client('connect')

unused = []


# checks if a user is currently assigned an extension
def has_extension(username):
    u = username

    response = table.query(
            IndexName='skIndex',
            KeyConditionExpression=Key('sk').eq('agentID') & Key('sk_value').eq(u))
    hasExt = response.get('Items', {})
# checks if the stored query result (hasExt) does not contain an item, in which case it returns false
    if (bool(hasExt)):
        return True 
    else:
        return False 
        

#TODO: paginate/iterate next tokens
def get_db_users():

    response = table.query(
    IndexName='skIndex',
    KeyConditionExpression=Key('sk').eq("agentID"))

    db_users = response.get('Items') 
    return db_users

    #for _ in items:
        #db_users.append(_.get(''))
    

# gets list of connect users, returns as list of dicts
def  get_users():
    users =[] 
    iid ='794790f5-0ae2-4348-806a-f58bf245ab3f'
    response = connect.list_users(
    InstanceId=iid,
    MaxResults=10
    )

    while "NextToken" in response:
        addUsers = response.get('UserSummaryList')

        for _ in addUsers:
            users.append(_.get('Username'))

        response = connect.list_users(
                NextToken=response["NextToken"],
                InstanceId=iid,
                MaxResults=10)

    for _ in response.get('UserSummaryList'):
        users.append(_.get('Username'))
    
    return users


# gets "not used (nu)" extensions 100 at a time
# TODO: raise exception when unable to find nu items
def get_unused_ext():
    global unused

    response = table.query(
    IndexName='skIndex',
    Limit=100,
    KeyConditionExpression=Key('sk').eq("nu"))

    items = response.get('Items') 

    for _ in items:
        unused.append(_.get('pk'))
        
    return 

def set_extension(username):
    u = username
    global unused

    if has_extension(username):
        print(username + " already has extension")#debug
        return
    if not bool(unused):
        get_unused_ext()

    extension = unused.pop()
# TODO: make conditional delete to verify that 'nu' item still exists
    response = table.delete_item(
        Key={
            'pk': extension,
            'sk': 'nu'
            }
    )
# add pk extension sk agentID
    response = table.put_item(
            Item={
                'pk': extension,
                'sk': 'agentID',
                'sk_value': username
            }
    )
    print(username + " added")#debug

    return


def update_db():
    users = get_users() 
    for _ in users:
        set_extension(_)
    return


# TODO: define return value
def lambda_handler(event, context):
    response = update_db()
    return response

users_old = get_db_users()
breakpoint()
