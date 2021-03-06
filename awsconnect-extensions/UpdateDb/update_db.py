import boto3
import json
import os
import logging
import csv
from boto3.dynamodb.conditions import Key,Attr

# constants/env vars
REGION = os.environ.get('AWS_REGION')
CONNECT_IID = os.environ.get('AWS_CONNECT_INSTANCEID')
TABLE_NAME = os.environ.get('AWS_TABLE')
BUCKET_NAME = os.environ.get('AWS_EXPORT_BUCKET')
# logger, env check, aws resources 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO refactor as for loop
if not REGION: logger.warning("Missing AWS_REGION Environmental Variable!")
if not CONNECT_IID: logger.warning("Missing AWS_CONNECT_INSTANCEID Environmental Variable!")
if not TABLE_NAME: logger.warning("Missing AWS_TABLE Environmental Variable!")
if not BUCKET_NAME: logger.warning("Missing AWS_EXPORT_BUCKET Environmental Variable!")

dynamodb = boto3.client('dynamodb', region_name = REGION) 
res_dynamodb = boto3.resource('dynamodb')
table = res_dynamodb.Table(TABLE_NAME)
connect = boto3.client('connect')
# global vars
unused = []
db_users = {}


def initialize_table():
    '''Initializes table with all available extensions.'''
    with table.batch_writer() as writer:
        for x in range(10000):
            extension = str(x)
            extension = extension.zfill(4)

            newItem = {
            "pk": extension,
            "sk": "nu",
            "sk_value": extension
            }

            response = writer.put_item(Item=newItem)
    return


def items_to_dict(items):
    '''Get dictionary from item list.'''
    d = {}
    for _ in items:
        d.update({_.get('sk_value'): _.get('pk')})
    return d


def get_db_users():
    '''Query table for all extensions in use by agents and store as global dictionary db_users'''
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


def get_users():
    '''Gets list of connect users, returns as set of usernames.'''
    users = set() 
    response = connect.list_users(
    InstanceId=CONNECT_IID,
    MaxResults=10
    )

    while "NextToken" in response:
        addUsers = response.get('UserSummaryList')

        for _ in addUsers:
            users.add(_.get('Username'))

        response = connect.list_users(
                NextToken=response["NextToken"],
                InstanceId=CONNECT_IID,
                MaxResults=10)

    for _ in response.get('UserSummaryList'):
        users.add(_.get('Username'))
    
    return users


def has_extension(username):
    '''Checks if a user is currently assigned an extension'''
    u = username
    if db_users == {}:
        get_db_users()

    hasExt = db_users.get(u)
    if (bool(hasExt)): # checks if the stored query result (hasExt) does not contain a value 
        return True 
    else:
        return False 


def remove_user(pk):
    '''Remove user by extension.'''
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

def get_unused_ext():
    '''Gets "not used (nu)" extensions 100 at a time.'''
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
    '''Allocate an extension for a single Connect user by passing their login name as a parameter.'''
    u = username
    global unused

    if has_extension(username):
        return
    if not bool(unused):
        get_unused_ext()

    extension = unused.pop()
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


def export_s3():
    '''Export a csv file of updated agents/extensions to S3 bucket specified by the BUCKET_NAME environment variable.'''
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)

    with open('/tmp/temp.csv', 'w', newline='') as data:
        fieldnames = ['user','extension']
        header = True
        writer = csv.writer(data)
        writer.writerow(fieldnames)
        
        for _ in db_users:
            writer.writerow([_ , db_users[_]]) 

    bucket.upload_file('/tmp/temp.csv', 'agent_extensions.csv')

    return


def update_db():
    '''Helper function to make lambda_handler as small as possible.'''
    users = get_users() 
    get_unused_ext()
    if not unused and users:
        initialize_table()

    for _ in users:
        set_extension(_)

    get_db_users()

    if len(db_users) > len(users):
        for _ in db_users:
            if _ not in users:
                remove_user(db_users[_])
                logger.info(_ + "[" + db_users[_] + "]: removed")
                db_users.pop(_)

    if BUCKET_NAME: 
        export_s3()

    return


def lambda_handler(event, context):
    '''The lambda_handler function doesn't curretly utilize the event or context parameters.'''
    update_db()
    return {
        'statusCode': 200,
        'body': json.dumps('Ok!')
    }
