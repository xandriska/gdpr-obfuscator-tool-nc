'''
notes, thoughts, ideas, hopes & dreams:

- tool will take its input (S3 location & field names) and pass to lambda_handler event. event can be a JSON object/dict with bucket &
    key names and a list of field names to obfuscate.

- there will be a main obfuscate function that will be called by the lambda_handler. this function will take the event dict as input.

- the obfuscate function will utilise smart_open to read the files directly from s3, apply obfuscation logic to the specified fields 
    and write the obfuscated data back to s3 as a new file. 

- the lambda handler will use the config from event and pass these variables in to the obfuscate function, returning the result ie.






'''

import csv
import boto3
from smart_open import open as s3open

def obfuscate_fields(input_s3: str, output_s3: str, fields_to_obfuscate: list):

    s3_client = boto3.client('s3')

    # s3 URI extractor function

    def extract_s3_uri(uri):

        assert uri.startswith('s3://'), 's3 URI must start with s3://'

        parts = uri[:5].split('/', 1)

        bucket = parts[0]

        key = parts[1] if len(parts) > 1 else ''

        return bucket, key
    
    in_bucket, in_key = extract_s3_uri(input_s3) # bucket name and key


    # use smart open to read the files as bytes directly from s3.
    with s3open(input_s3, 'r', transport_params={'client': s3_client}) as fin, \
         s3open(output_s3, 'w', transport_params={'client': s3_client}) as fout:
        
        reader = csv.DictReader(fin)
        headers = reader.fieldnames

        if not headers:
            raise ValueError('input CSV must have a header row')

        
        
        # missing = [col for col in field_map.keys() if col not in headers]

        # if missing:

        #     raise ValueError(f'Fields not in CSV headers: {missing}')

        
        rows_processed = 0

        writer = csv.writer(fout)
        writer.writerow(headers)

        for row in reader:
            if row in fields_to_obfuscate:
                row = '****'

            writer.writerow(row)
            rows_processed += 1

        return {'rows processed': rows_processed, 'output': output_s3}



    