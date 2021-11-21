import json
import boto3
from boto3.dynamodb.conditions import Key


def get_agent_id(Extension, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('AgentData')
    response = table.query(
        KeyConditionExpression=Key('pk').eq(str(Extension)) & Key('sk').eq('agentID')
    )
    return response['Items']


def lambda_handler(event, context):
    Extension = event['Details']['Parameters']['pk']
    agentID = get_agent_id(Extension)
    for agent in agentID:
        print(agent['pk'], ":", agent['sk_value'])
        
           
    return agent
