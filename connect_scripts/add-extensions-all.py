import pdb
import boto3
import json
from boto3.dynamodb.conditions import Key,Attr

# TODO:function to check if agent has an extension, function to assign extension, and check function for exception handling and readability
 
dynamodb = boto3.client('dynamodb', region_name = 'us-east-1') 
res_dynamodb = boto3.resource('dynamodb')
table = res_dynamodb.Table('AgentData')

connect = boto3.client('connect')

unused = []



# checks if a user is currently assigned an extension 
# checks if a user is currently assigned an extension
#TODO: broken - key's sk should equal username and pk should equal agentID or such
def has_extension(username):
    u = username

    response = table.query(
            IndexName='byAgent',
            KeyConditionExpression=Key('pk').eq(u))
    hasExt = response.get('Items', {})

    if (bool(hasExt)):
        return False 
    else:
        return True 
        

# gets list of connect users, returns as list of dicts
# TODO: broken users var
def  get_users():
    users = {}
    items = []
    iid ='794790f5-0ae2-4348-806a-f58bf245ab3f'
    response = connect.list_users(
    InstanceId=iid,
    MaxResults=10
    )

    while "NextToken" in response:
        addUsers = response.get('UserSummaryList')

        users.update(addUsers)

        response = connect.list_users(
                NextToken=response["NextToken"],
                InstanceId=iid,
                MaxResults=10)

    users.update(response.get('UserSummaryList'))
    
    breakpoint()
    return users


# gets unused extensions 100 at a time
# gets "not used (nu)" extensions 100 at a time
#TODO: only return pk and sk as sk_value is the same as pk for these items
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


#TODO: test 
def set_extension(username):
    u = username
    global unused

    if not bool(unused):
        get_unused_ext()

    extension = unused.pop()
# TODO: make transactional delete checking for any other items using same 'pk'
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


    return

#get_unused_ext()
get_users()
breakpoint()
