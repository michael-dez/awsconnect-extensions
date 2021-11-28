import json
import boto3
import os
from boto3.dynamodb.conditions import Key

TABLE_NAME=os.environ.get('AWS_TABLE')

def get_agent_id(Extension, dynamodb=None):
    '''Query extension table by extension and return Items dictionary containing agent login.'''
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression=Key('pk').eq(str(Extension)) & Key('sk').eq('agentID')
    )
    return response['Items']


def lambda_handler(event, context):
    '''Retrieves extension from event, calls get_agent_id, and returns agent login from returned dictionary.'''
    Extension = event['Details']['Parameters']['pk']
    agentID = get_agent_id(Extension)
    for agent in agentID:
        print(agent['pk'], ":", agent['sk_value'])
        
           
    return agent
