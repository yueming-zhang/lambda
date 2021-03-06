import sys, os, inspect, pathlib 
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = f"{pathlib.Path(currentdir).parent.parent.absolute()}/"
sys.path.insert(0,parentdir)

import json
import pytest
from news_sentiment_app import app, query


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{ "test": "body"}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }


def test_lambda_news_handler(apigw_event, mocker):

    ret = app.lambda_handler({'action':'insert news'}, "")
    data = json.loads(ret['body'])
    assert ret['statusCode'] == 200
    assert data['insert count'] > 0

    ret = app.lambda_handler({'action':'delete news'}, "")

    data = json.loads(ret['body'])
    assert ret['statusCode'] == 200
    assert data['delete count'] > 0


def test_lambda_news_delete2():    
    ret = app.lambda_handler({'action':'delete news'}, "")
    ret = app.lambda_handler({'action':'delete news'}, "")
    data = json.loads(ret['body'])

    assert ret['statusCode'] == 200
    assert data['delete count'] == 0


def test_get_by_sentiment():
    #insert some news
    ret = app.lambda_handler({'action':'insert news'}, "")

    ret = query.lambda_handler({'sentiment':'NEUTRAL'}, "")

    assert ret['statusCode'] == 200
    ret = json.loads(ret['body'])

    assert ret['ResponseMetadata']['HTTPStatusCode'] == 200
    assert 'Items' in ret
    assert len(ret['Items']) > 0

    assert ret['Items'][0]['sentiment'] == 'NEUTRAL'
