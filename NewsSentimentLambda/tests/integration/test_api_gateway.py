import os
from unittest import TestCase

import boto3
import requests
import json

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out what the NewsApi URL is
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "NewsApi"]
        self.assertTrue(api_outputs, f"Cannot find output NewsApi in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]

        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "SentimentApi"]
        self.assertTrue(api_outputs, f"Cannot find output NewsApi in stack {stack_name}")
        self.api_endpoint_get_sentiment = api_outputs[0]["OutputValue"]

    def test_api_gateway_delete(self):
        """
        Call the API Gateway endpoint and check the response
        """
        ret = requests.get(self.api_endpoint)

        assert ret.status_code == 200
        data = json.loads(ret.text)
        assert data['delete count'] >= 0


    def test_api_gateway_insert(self):
        """
        Call the API Gateway endpoint and check the response
        """
        ret = requests.get(self.api_endpoint, params={'action':'insert news'})

        assert ret.status_code == 200
        data = json.loads(ret.text)
        assert data['insert count'] >= 0

        inserted = data['insert count']
        ret = requests.get(self.api_endpoint) #default is deletion
        assert ret.status_code == 200
        data = json.loads(ret.text)
        assert data['delete count'] == inserted

    def test_api_gateway_get_sentiment(self):
        """
        Call the API Gateway endpoint and check the response
        """
        ret = requests.get(self.api_endpoint_get_sentiment, params={'sentiment':'NEGATIVE'})

        assert ret.status_code == 200
        data = json.loads(ret.text)
        assert 'Items' in data
        assert data
        assert data['ResponseMetadata']['HTTPStatusCode'] == 200
