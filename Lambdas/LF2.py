import boto3
import json
import requests
import random
from requests_aws4auth import AWS4Auth

def receiveMsgFromSqsQueue():
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/679536496490/Q1'
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=5,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )
    return response

# The function return list of business id
def findRestaurantFromElasticSearch(cuisine):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session(aws_access_key_id="",
                          aws_secret_access_key="", 
                          region_name="us-east-1").get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'search-restaurants-g7syvrxcwt3lgf4ce55vgsrjtu.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = 'https://' + host + '/' + index + '/_search'
    # Getting 3 business IDs from ElasticSearch
    query = {
        "size": 1300,
        "query": {
            "query_string": {
                "default_field": "cuisine",
                "query": cuisine
            }
        }
    }
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    noOfHits = res['hits']['total']
    hits = res['hits']['hits']
    print(noOfHits)
    print(hits[0]['_id'])
    restaurant_id = []
    for hit in hits:
        print(hit)
        restaurant_id.append(str(hit['_source']['restaurant_id']))
    print(len(restaurant_id))
    return restaurant_id

# function returns detail of all resturantids as a list(working)
def getRestaurantFromDb(restaurantIds):
    res = []
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')
    for id in restaurantIds:
        response = table.get_item(Key={'id': id})
        res.append(response)
    return res

def getMsgToSend(restaurantDetails,message):
    noOfPeople = message['MessageAttributes']['CountPeople']['StringValue']
    date = message['MessageAttributes']['DiningDate']['StringValue']
    time = message['MessageAttributes']['DiningTime']['StringValue']
    cuisine = message['MessageAttributes']['Cuisine']['StringValue']
    resOneName = restaurantDetails[0]['Item']['name']
    resOneAdd = restaurantDetails[0]['Item']['location']
    resTwoName = restaurantDetails[1]['Item']['name']
    resTwoAdd = restaurantDetails[1]['Item']['location']
    resThreeName = restaurantDetails[2]['Item']['name']
    resThreeAdd = restaurantDetails[2]['Item']['location']
    msg = f"Hello! Here are my {cuisine} restaurant suggestions for {noOfPeople} people, for {date} at {time}:" + "\n" + f"1. {resOneName}, located at {resOneAdd}," + "\n" + f"2. {resTwoName}, located at {resTwoAdd}," + "\n" + f"3. {resThreeName}, located at {resThreeAdd}." + "\n" + "Enjoy your meal!"
    return msg
def sendEmail(msgToSend,EmailAddress):
    client = boto3.client("ses")
    clientDB = boto3.client('dynamodb')
    clientDB.put_item(TableName='previousState', Item={'cuisines':{'S':"1"}, 'msg':{'S':msgToSend}})
    client.send_email(
        Destination={
            "ToAddresses": [
                EmailAddress,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": msgToSend,
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Your Dining Recommendations Are Here!",
            },
        },
        Source="bsb9397@nyu.edu",
    )
    
def deleteMsg(receipt_handle):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/679536496490/Q1'
    sqs.delete_message(QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
    )

def lambda_handler(event, context):
    # getting response from sqs queue
    sqsQueueResponse = receiveMsgFromSqsQueue()
    if "Messages" in sqsQueueResponse.keys():
        for message in sqsQueueResponse['Messages']:
            cuisine = message['MessageAttributes']['Cuisine']['StringValue']
            restaurantIds = findRestaurantFromElasticSearch(cuisine)
            # Assume that it returns a list of restaurantsIds
            # call some random function to select 3 from the list
            restaurantIds = random.sample(restaurantIds, 3)
            restaurantDetails = getRestaurantFromDb(restaurantIds)
            # now we have all required details to send the sms
            # now we will create the required message using the details
            msgToSend = getMsgToSend(restaurantDetails,message)
            print(msgToSend)
            EmailAddress = message['MessageAttributes']['EmailAddress']['StringValue']
            sendEmail(msgToSend,EmailAddress)
            #now delete message from queue
            receipt_handle = message['ReceiptHandle']
            deleteMsg(receipt_handle)
            return "Recommendation sent"