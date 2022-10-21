import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("previousState")
    res = table.get_item(Key={'cuisines': "1"})
    print(res)
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText',
                'content': res['Item']['msg']}
        }
    }
