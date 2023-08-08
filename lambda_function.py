import boto3
import json
from custom_encoder import CustomEncoder
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define our dynamodb table
dynamodbTableName = 'userserverless'

#define our dynamo clients
dynamodb = boto3.resource('dynamodb')

#define our table
table = dynamodb.Table(dynamodbTableName)

#define our methods
getMethod = 'GET'
postMethod = 'POST'
putMethod = 'PUT'
deleteMethod = 'DELETE'

#define our Paths
healthPath = '/health'
productPath = '/user'
productsPath = '/users'

# entry point for our lambda function
def lambda_handler(event, context):
    logger.info(event) #log the request event to see how the request looks like
    httpMethod = event['httpMethod'] #extract the http method from our event object
    path = event['path'] #extract the path
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['id'])
    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))
    elif httpMethod == putMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody)
    elif httpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['id'])
    else:
        response = buildResponse(404, 'Not found')
    

    return response

def getProduct(productId):
    try:
        response = table.get_item(
            Key={
                'id': productId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'ProductId %s not found' % productId})
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')

def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'products': result
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')

def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('sorry your item wasnt ')

def modifyProduct(event):
    
    try:
        
        response = table.update_item(
            
            
            Key={
                'id': event['id']
            },
            UpdateExpression='SET fname=:pn, lname= :pnum ,username=:pb, email=:d , avatar= :a',
            ExpressionAttributeValues={
                ':pn': event['fname'],
                ':pnum':event['lname'],
                ':pb':event['username'],
                ':d':event['email'],
                ':a': event['avatar'],
            },
            ReturnValues='UPDATED_NEW'
        )
        
       
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdateAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')

def deleteProduct(productId):
    try:
        response = table.delete_item(
            Key={
                'id': productId
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
            
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
        
    return response
