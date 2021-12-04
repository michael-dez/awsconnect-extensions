
# Amazon Connect Extensions

This project aims to simplify setting up agent to agent calls for an Amazon Connect instance.  It has been designed largely around the Lambda function from [this AWS Knowledge Center article.](https://aws.amazon.com/premiumsupport/knowledge-center/connect-agent-to-agent-extensions/) Some additional [configuration](##Configuration) of the Amazon Connect instance is required after deployment.
## Features
* Call/transfer to available agents by extension
* Scheduled (hourly) allocation/deallocation of extensions
* Export to S3 as .csv
* Fast deployment and rollback via AWS SAM/CloudFormation
## Limitations
* Calls will only connect to agents in the "Available" status due to all other statuses being not [routable](https://docs.aws.amazon.com/connect/latest/adminguide/agent-custom.html).  
* Calls made directly to agents take priority over all other queues
## Prerequisites
* An Amazon Connect instance
* An S3 bucket for export
## Deployment
### Serverless Application Repository (Console)
1. Navigate to the [repository.](https://serverlessrepo.aws.amazon.com/applications/us-east-1/828393986024/awsconnect-extensions)
2. Select deploy and enter the requested parameters.
### AWS SAM CLI
Note: Requires installation of the [sam cli](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
1. Clone the repository.
2. From the root of the project directory run ```sam deploy --guided```
3. Use the ARN of the Connect instance for `ConnectParam`, the desired table name for `TableParam`, and an existing bucket for `BucketParam` to export the csv.
## Configuration
1. Add the GetAgent Lambda to your Amazon Connect instance from the Contact Flows tab in the instance overview.
2. Download both contact flows located in the `contact-flows` directory.
3. Create a new customer queue flow and import the agent-queue contact flow. Choose a name, then save and publish.
4. Create a new contact flow and import the inbound-contact-flow. Select the GetAgent Lambda as the Function ARN in the Invoke AWS Lambda function block. Select the new customer queue flow in the ***Set customer queue flow block*** then save and publish.
5. associate a DID phone number to the new inbound contact flow.
## Contribute
* [Pull requests](https://help.github.com/articles/using-pull-requests/) are welcome.

