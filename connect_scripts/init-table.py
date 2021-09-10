import boto3

dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
table = dynamodb.Table('AgenttoAgent')

for x in range(10000):
    extension = str(x)
    extension = extension.zfill(4)
        
    newItem = {
    "Extension": extension,
    "AgentLoginName": "",
    "InUse": False 
    }
    response = table.put_item(Item=newItem)
    print(newItem)
    print(response)
    
