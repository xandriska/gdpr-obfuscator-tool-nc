import boto3


def get_file_from_s3(s3_client):
    response = (s3_client.get_object(Bucket='bucket-name', Key='file-key'))

    return response['Body'].read().decode('utf-8')
