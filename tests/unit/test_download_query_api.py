import boto3
import pytest
import unittest

from operator import contains
from moto import mock_s3

from sds_in_a_box.SDSCode.download_query_api import lambda_handler


@pytest.mark.network
class TestIndexer(unittest.TestCase):

    @mock_s3
    def setUpS3(self):
        self.bucket_name = "download-query-api"
        self.s3_client = boto3.client("s3")

        # create mock s3 bucket
        self.s3_client.create_bucket(Bucket=self.bucket_name,
                              CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
                              )
        # upload a file
        self.s3_filepath = "test-data/science_block_20221116_163611Z_idle.bin"
        self.local_filepath = "tests/unit/test-data/science_block_20221116_163611Z_idle.bin"
        self.s3_client.upload_file(self.local_filepath, self.bucket_name, self.s3_filepath)
        file_list = self.s3_client.list_objects(Bucket=self.bucket_name)['Contents']

        assert len(file_list) == 1

    @mock_s3
    def test_object_exists_with_bucket_and_path(self):
        """Test that objects exist in s3
        """
        self.setUpS3()
        self.event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": f"filename={self.s3_filepath}&bucket={self.bucket_name}",
            "queryStringParameters": {
                "s3_uri": f"s3://{self.bucket_name}/{self.s3_filepath}",
                "bucket": f"{self.bucket_name}",
                "filepath": f"{self.s3_filepath}"
            }
        }

        response = lambda_handler(event=self.event, context=None)
        assert response['statusCode'] == 200
        assert contains(response['body'], 'download_url')

    @mock_s3
    def test_object_exists_with_bucket_and_path_fails(self):
        """Test that objects exist in s3
        """
        self.setUpS3()
        self.event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": f"filename={self.s3_filepath}&bucket={self.bucket_name}",
            "queryStringParameters": {
                "bucket": f"{self.bucket_name}",
                "filepath": "/bad_path/fake.txt"
            }
        }

        response = lambda_handler(event=self.event, context=None)
        assert response['statusCode'] == 404

    @mock_s3
    def test_object_exists_with_s3_uri(self):
        """Test that objects exist in s3
        """
        self.setUpS3()
        self.event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": f"s3_uri=s3://{self.bucket_name}/{self.s3_filepath}",
            "queryStringParameters": {
                "s3_uri": f"s3://{self.bucket_name}/{self.s3_filepath}"
            }
        }

        response = lambda_handler(event=self.event, context=None)
        assert response['statusCode'] == 200
        assert contains(response['body'], 'download_url')
    
    @mock_s3
    def test_object_exists_with_s3_uri_fails(self):
        """Test that objects exist in s3
        """
        self.setUpS3()
        self.event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": f"s3_uri=s3://{self.bucket_name}/bad_path/bad_file.txt",
            "queryStringParameters": {
                "s3_uri": f"s3://{self.bucket_name}/bad_path/bad_file.txt"
            }
        }

        response = lambda_handler(event=self.event, context=None)
        assert response['statusCode'] == 404

    @mock_s3
    def test_input_parameters_missing(self):
        """Test that required input parameters exist
        """
        self.setUpS3()
        self.empty_para_event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": ""
        }

        self.missing_para_event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": f"filename={self.s3_filepath}",
            "queryStringParameters": {
                "filepath": f"{self.s3_filepath}"
            }
        }

        response = lambda_handler(event=self.empty_para_event, context=None)
        assert response['statusCode'] == 421

        response = lambda_handler(event=self.missing_para_event, context=None)
        assert response['statusCode'] == 422


if __name__ == '__main__':
    unittest.main()
