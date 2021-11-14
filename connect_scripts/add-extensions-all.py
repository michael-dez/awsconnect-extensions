import boto3
import json
import os
import logging
from boto3.dynamodb.conditions import Key,Attr

# TODO: convert has_extension function to utilize 1 user query from get_db_users
# , backoff algorithm for connect api request in get_user (?), logging
 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.client('dynamodb', region_name = 'us-east-1') 
res_dynamodb = boto3.resource('dynamodb')
table = res_dynamodb.Table('AgentData')

connect = boto3.client('connect')

unused = []
db_users = {}


# checks if a user is currently assigned an extension
def has_extension(username):
    u = username

    response = table.query(
            IndexName='skIndex',
            KeyConditionExpression=Key('sk').eq('agentID') & Key('sk_value').eq(u))
    hasExt = response.get('Items', {})
    if (bool(hasExt)): # checks if the stored query result (hasExt) does not contain an item, in which case it returns false
        return True 
    else:
        return False 


# add response items to a dict (returned)
def items_to_dict(items):
    d = {}
    for _ in items:
        d.update({_.get('sk_value'): _.get('pk')})
    return d


#TODO: test with query that produces Last Evaluated Key 
def get_db_users():
    global db_users
    response = table.query(
    IndexName='skIndex',
    ProjectionExpression='sk_value, pk',
    KeyConditionExpression=Key('sk').eq('agentID'))
    
    if response.get('Count') < 1:
        return

    while "LastEvaluatedKey" in response:
        u = items_to_dict(response.get('Items'))
        db_users.update(u)

        response = table.query(
            IndexName='skIndex',
            ExclusiveStartKey=response["LastEvaluatedKey"],
            ProjectionExpression='sk_value, pk',
            KeyconditionExpression=Key('sk').eq("agentID"))

    db_users.update(items_to_dict(response.get('Items')))
    return db_users


# gets list of connect users, returns as set of usernames
def get_users():
    users = set() 
    iid ='794790f5-0ae2-4348-806a-f58bf245ab3f'
    response = connect.list_users(
    InstanceId=iid,
    MaxResults=10
    )

    while "NextToken" in response:
        addUsers = response.get('UserSummaryList')

        for _ in addUsers:
            users.add(_.get('Username'))

        response = connect.list_users(
                NextToken=response["NextToken"],
                InstanceId=iid,
                MaxResults=10)

    for _ in response.get('UserSummaryList'):
        users.add(_.get('Username'))
    
    return users


# remove user by extension
#TODO: test, should accept a list of users for batch operations; make conditional 
def remove_user(pk):
    response = table.delete_item(            
        Key={
            'pk': pk,
            'sk': 'agentID'
            }
    )

    response = table.put_item(
            Item={
                'pk': pk,
                'sk': 'nu'
            }
    )

    return

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

    if not unused:
        logger.warning("No unused extensions found.")
        
    return 

def set_extension(username):
    u = username
    global unused

    if has_extension(username):
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
    logger.info(username + ": added")#debug

    return


def update_db():
    users = get_users() 

    for _ in users:
        set_extension(_)

    get_db_users()

    if len(db_users) > len(users):
        for _ in db_users:
            if _ not in users:
                remove_user(db_users[_])
                logger.info(_ + "[" + db_users[_] + "]: removed")#debug

    return


# TODO: define return value
def lambda_handler(event, context):
    update_db()
    return
