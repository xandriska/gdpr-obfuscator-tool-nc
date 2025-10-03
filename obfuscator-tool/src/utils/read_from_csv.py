import csv
import io

import boto3

from src.utils.get_file_from_s3 import get_file_from_s3

'''
reads a bytes file passed in from s3 and returns a csv.dictreader object.

'''

# when bringing in bytes file from s3 use string.io blah to convert to string before working with dictreader and dictwriter methods

# then specific columns/rows can be accessed by name or index

def process_csv():

   with open('crocodile_dataset.csv', 'r', newline='') as file:

    csv_reader = csv.DictReader(file)

    for row in csv_reader:
        print(row['Common Name'])

#process_csv(get_file_from_s3(boto3.client('s3'), 'gdpr-dummy-bucket', 'dummy-folder/crocodile_dataset.csv'))

process_csv()