import os
from unittest import TestCase

import boto3
import requests

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
        here we use cloudformation API to find out what the HelloWorldApi URL is
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation", region_name='us-east-1')

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "HelloWorldApi"]
        self.assertTrue(api_outputs, f"Cannot find output HelloWorldApi in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]
        print (f'{self.api_endpoint=}')

        # second API: HelloWorldApi_1
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "SecuredHelloWorldAPI"]
        self.assertTrue(api_outputs, f"Cannot find output HelloWorldApi in stack {stack_name}")
        self.api_endpoint_1 = api_outputs[0]["OutputValue"]


    def test_api_gateway(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint)
        assert response.status_code == 200
        self.assertDictEqual(response.json(), {"message": "hello world: 123"})
        #assert len(response.json()['message']) > 10

    def test_secured_api_gateway_unsigned(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint_1)
        assert response.status_code == 403

    def test_secured_api_gateway_signed(self):
        """
        Call the API Gateway endpoint and check the response
        """
        headers = {"x-api-key": "abcdefg123456665ffghsdghfgdhfgdh4565"}#should pass through output

        response = requests.get(self.api_endpoint_1, headers=headers)
        assert response.status_code == 200
        assert len(response.json()['message']) > 10
        assert len(response.json()['message'][0]) > 10

