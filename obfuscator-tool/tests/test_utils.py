import moto
import boto3

from src.utils.get_file_from_s3 import get_file_from_s3

def test_get_file_from_s3():
    # Mock S3 service
    with moto.mock_aws():
        test_client = boto3.client('s3')
        test_bucket_name = 'bucket-name'
        test_file_key = 'file-key'
        test_file_content = 'sample content'

        # Create a mock bucket and upload a file
        test_client.create_bucket(Bucket=test_bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2'})
        test_client.put_object(Bucket=test_bucket_name, Key=test_file_key, Body=test_file_content)

        # Call the function
        result = get_file_from_s3(test_client)

        # Assert the file is as expected
        assert result == test_file_content