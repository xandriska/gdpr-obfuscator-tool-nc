from obfuscate import obfuscate_fields

'''

Example event shapes supported:
    1) Direct: event contains 'input_s3','output_s3','fields' list:
       {
         "file_to_obfuscate": 's3://my_ingestion_bucket/new_data/file1.csv',
         "output_s3": 's3://obfuscated_files/csv/file1obfuscated.csv',
         "pii_fields": ['name', 'email_address'],
       }

'''

def lambda_handler(event, context):

    cfg = event

    input_s3 = cfg['file_to_obfuscate']

    output_s3 = cfg['output_s3']

    field_list = cfg['pii_fields']

    return obfuscate_fields(input_s3, output_s3, field_list)
    