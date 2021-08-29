import boto3

dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
table = dynamodb.Table('AgenttoAgent')

newItem = {
    "Extension": "0000",
    "AgentLoginName": "",
    "InUse": True
    }
response = table.put_item(Item=newItem)
print(response)
