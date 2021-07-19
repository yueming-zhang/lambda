import boto3
import sys
from boto3.dynamodb.conditions import Key
import json

#Best practice is to create the boto3 connections in the global section
#and not inside the handler - More on this in the future lecturees
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # TODO implement
    #*******************************************************************#
    # Thanks to MEDVEDED DENIS, one of the student to bring this        #
    # into my attention!                                                #
    # It is NOT efficient to initialize db connections in handler.      #
    # Hence the below line is commented on 02/2020 and moved to the     # 
    # global section.                                                    #
    #*******************************************************************#
    #dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table('news')
    print ('in sentiment lambda, event is :')
    print (event)
    inputSentiment='NETURAL'
    if 'sentiment' in event:
        inputSentiment = event['sentiment']
    elif 'queryStringParameters' in event and event['queryStringParameters'] != None:
        if 'sentiment' in event['queryStringParameters']:
            inputSentiment = event['queryStringParameters']['sentiment']

    try:
        # Querying the table using Primary key
        if inputSentiment != None:
            response = table.query(
                IndexName='sentiment-index',
                KeyConditionExpression=Key('sentiment').eq(inputSentiment),
                Limit=10, #limits returned news to 10
                ScanIndexForward=False) #descending order of timestamp, most recent news first
        else:
            response = table.scan(Limit=10)

        print('query done, result is')
        print(response)
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except:
        print("Unexpected error:", sys.exc_info()[0])        
        raise
