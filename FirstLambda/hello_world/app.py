import json
import numpy as np
import boto3

def lambda_handler(event, context):
    x = np.arange(0, 10, 2)
    y = np.arange(5)
    m = np.vstack([x, y])

    print (f'numpy calculation result: {m}')

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"hello world: 123",
        }),
    }



def lambda_handler_1(event, context):
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')

    bucket_list = [bucket["Name"] for bucket in response['Buckets']]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": bucket_list
        }),
    }
