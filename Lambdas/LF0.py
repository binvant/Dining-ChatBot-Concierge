import json

def lambda_handler(event, context):
    return{
        'statusCode' : 200,
        
        'headers':{
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            
        },
        'body':{'messages':[{'unstructured':{'text':'Application under development. Search functionality will be implemented in Assignment 2.'}, 'type':'unstructured'}]}
    }