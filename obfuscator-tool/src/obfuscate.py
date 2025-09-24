import csv
import io
import hashlib
from typing import Dict, Any, List

import boto3

def obfuscate_file(input: Dict[str, Any]) -> bytes:
    """
    Obfuscate sensitive data in a CSV file stored in S3.

    Args:
        input (Dict[str, Any]): A dictionary containing:
            - bucket (str): The S3 bucket name.
            - key (str): The S3 object key.
            - columns_to_obfuscate (List[str]): List of column names to obfuscate.

    Returns:
        bytes: The obfuscated CSV content as bytes.
    """
    s3 = boto3.client('s3')
    bucket = input['bucket']
    key = input['key']
    columns_to_obfuscate = input['columns_to_obfuscate']

    # Download the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    file_content = response['Body'].read().decode('utf-8')

    # Read the CSV content
    csv_reader = csv.DictReader(io.StringIO(file_content))
    output = io.StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=csv_reader.fieldnames)
    csv_writer.writeheader()

    # Obfuscate specified columns
    for row in csv_reader:
        for column in columns_to_obfuscate:
            if column in row and row[column]:
                # Simple obfuscation using SHA256 hash
                row[column] = hashlib.sha256(row[column].encode()).hexdigest()
        csv_writer.writerow(row)

    return output.getvalue().encode('utf-8')