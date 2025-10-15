import boto3

from obfuscate import obfuscate_fields

'''

Example event shape:
       {
         "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
         "output_s3": "s3://obfuscated_files/csv/file1obfuscated.csv",
         "pii_fields": ["name", "email_address"]
       }

'''
s3_client = boto3.client('s3')

def lambda_handler(event, context):

    input_s3 = event['file_to_obfuscate']

    output_s3 = event['output_s3']

    fields = event['pii_fields']

    return obfuscate_fields(input_s3, output_s3, fields, s3_client)
    