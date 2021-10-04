import boto3

dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
table = dynamodb.Table('AgentData')

for x in range(10000):
    extension = str(x)
    extension = extension.zfill(4)
        
    newItem = {
    "pk": extension,
    "sk": "nu",
    "sk_value": extension
    }

    response = table.put_item(Item=newItem)
    print(newItem)
    print(response)
    
