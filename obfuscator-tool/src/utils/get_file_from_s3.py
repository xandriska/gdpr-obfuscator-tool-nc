

'''
retrieves a file from an s3 bucket. boto3 client passed in as arg.

'''


def get_file_from_s3(s3_client, bucket, key) -> bytes:
    response = (s3_client.get_object(Bucket=bucket, Key=key))

    return response['Body'].read()
