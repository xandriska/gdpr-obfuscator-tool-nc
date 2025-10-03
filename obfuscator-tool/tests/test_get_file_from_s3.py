import moto
import boto3

from src.utils.get_file_from_s3 import get_file_from_s3

def test_bucket_exists():
    # Mock S3 service
    with moto.mock_aws():
        test_client = boto3.client('s3')
        test_bucket_name = 'bucket-name'
        test_file_key = 'file-key'
        test_file_content = 'test content'

        # Create a mock bucket and list it
        test_client.create_bucket(Bucket=test_bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2'})
        
        response = test_client.list_buckets()

        # Output the bucket names
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')
        

        # Call the function
        result = get_file_from_s3(test_client)

        # Assert the file is as expected
        assert 