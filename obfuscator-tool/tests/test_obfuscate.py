
import csv
import io
import pytest
import boto3
from moto import mock_aws

import src.obfuscate
from src.obfuscate import obfuscate_fields


'''
unit testing for obfuscate function.

core functionality:

- opens and reads a csv file from s3 using smart_open.
- creates a DictReader object ('reader') from the input file.
- extracts the header row from the csv file ('headers')
- raises a valueerror if no header row present
- iterates over every row in the csv file as dict
- creates a copy of each row
- for each item (field) in the list of fields to obfuscate, compare that field
with each row (from the copy). the field will correspond to a key in out_row. if
any field is the same as a key, access that key, and change its value to '****'.

- so if a row in out_row looks like: {'name': bob, 'email': 'bob@home.com'}

- the 'name' and 'email' fields will be changed to 'name': ****, email: ****.

- writes these changed fields with the original headers to a new file ('fout') and 
puts it into s3 


'''

# test that obfuscator opens and reads a file from s3
# test that obfuscator writes a file to s3
# test that it creates a dictreader object from infile
# test that it raises a valueerror if no headers in infile
# test that it writes a new csvfile with the same headers as infile
#           it obfuscates fields correctly

# expected_output = """Customer,Flavour,Size,Price
#         ****,Chocolate,****,3.50
#         ****,Vanilla,****,1.80
#         ****,Strawberry,****,2.50
#         # ****,Mint Choc Chip,****,3.70"""

def test_obfuscate_opens_csv(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"
    
    test_output = "s3://test-bucket/output.csv"

    test_fields = ['Customer', 'Size']

    def fake_open(uri, mode='r', transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""


        if uri == "s3://test-bucket/input.csv" and mode == 'r':
            return io.StringIO(fake_csv)
        elif uri == "s3://test-bucket/output.csv" and mode == 'w':
            return io.StringIO()

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open)

    # act

    result = obfuscate_fields(test_input, test_output, test_fields, s3_client=None)

    # assert

    assert result["rows processed"] == 4


@mock_aws
def test_obfuscate_reads_writes_from_s3():

    # arrange

    test_input = "s3://test-bucket/input.csv"
    
    test_output = "s3://test-bucket/output.csv"

    test_fields = ['Customer', 'Size']

    test_client = boto3.client('s3')

    location = {'LocationConstraint': 'eu-west-2'}

    test_bucket = 'test-bucket'

    test_client.create_bucket(Bucket=test_bucket, CreateBucketConfiguration=location)

    input_key = 'input.csv'

    output_key = 'output.csv'

    fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""
    
    test_client.put_object(Bucket=test_bucket, Key=input_key, Body=fake_csv)

    # act

    result = obfuscate_fields(
        test_input, test_output,
        test_fields, s3_client=test_client
    )

    # assert

    response = test_client.get_object(Bucket=test_bucket, Key=output_key)

    output_csv = response["Body"].read().decode("utf-8")

    assert output_csv != fake_csv

