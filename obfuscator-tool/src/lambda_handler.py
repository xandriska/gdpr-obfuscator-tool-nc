"""

This lambda handler function connects to AWS and passes the
supplied JSON event shape to the obfuscate_fields function.

The event requires an input location in the form of an
S3 bucket URI.

An output location is optional.

The "pii_fields" key must be supplied with a list (example below)
containing the names of all the data fields that require obfuscation.

An error will occur if no input and/or PII fields are supplied.

Example event shapes:
       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "output_s3": "s3://obfuscated_files/csv/file1obfuscated.csv",
         "pii_fields": ["name", "email_address"]
       }

       --

       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "pii_fields": ["name", "email_address"]
       }

       --

       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "output_s3": "",
         "pii_fields": ["name", "email_address"]
       }

"""

import boto3

from src.obfuscate import obfuscate_fields

s3_client = boto3.client("s3")


def lambda_handler(event, context):

    try:
        input_s3 = event["input_s3"]
    except KeyError:
        return {"status": "error", "message": "'input_s3' key is required"}

    output_s3 = event.get("output_s3")

    fields = event.get("pii_fields")
    if not fields:
        return {
            "status": "error",
            "message": "'pii_fields' key is required and cannot be empty",
        }

    return obfuscate_fields(input_s3, output_s3, fields, s3_client)
