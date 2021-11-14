import boto3
import json
import os
import logging
from boto3.dynamodb.conditions import Key,Attr

region = os.environ.get('AWS_REGION')
connect_iid = os.environ.get('AWS_CONNECT_INSTANCEID')
table_name = os.environ.get('AWS_CONNECT_TABLE')
# logger, env check, aws resources 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if not region: logger.warning("Missing AWS_REGION Environmental Variable!")
if not connect_iid: logger.warning("Missing AWS_CONNECT_INSTANCEID Environmental Variable!")
if not table_name: logger.warning("Missing AWS_CONNECT_TABLE Environmental Variable!")
dynamodb = boto3.client('dynamodb', region_name = region) 
res_dynamodb = boto3.resource('dynamodb')
table = res_dynamodb.Table(table_name)
connect = boto3.client('connect')
# global vars
unused = []
db_users = {}


# get dictionary from item list
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
                InstanceId=connect_iid,
                MaxResults=10)

    for _ in response.get('UserSummaryList'):
        users.add(_.get('Username'))
    
    return users


# checks if a user is currently assigned an extension
def has_extension(username):
    u = username
    if db_users == {}:
        get_db_users()

    hasExt = db_users.get(u)
    if (bool(hasExt)): # checks if the stored query result (hasExt) does not contain a value 
        return True 
    else:
        return False 


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
    logger.info(username + ": added")

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
                logger.info(_ + "[" + db_users[_] + "]: removed")

    return


# TODO: a return value would be nice 
def lambda_handler(event, context):
    update_db()
    return
