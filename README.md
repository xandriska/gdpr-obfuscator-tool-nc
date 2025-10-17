# GDPR Obfuscator

## Compatible with AWS (S3) and .CSV

A small Python tool which obfuscates sensitive data in .csv files from S3 Buckets. Built as a freelance project for Tech Returners via Northcoders.

**Description**

Supply the tool with the fields you wish to anonymise in the form of a JSON event in AWS Lambda. The tool will convert all data in those fields to '\*\*\*\*' and stream the newly obfuscated data to a file output location of your choosing (or provide a default location if none is given).

Designed to be deployed via AWS Lambda. Unit tested with monkeypatch and Moto.

# Usage

The tool implements a lambda handler function which connects to AWS. The lambda handler expects an event in the form of a JSON. Any of the below example formats are acceptable:

```
       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "output_s3": "s3://obfuscated_files/csv/file1obfuscated.csv",
         "pii_fields": ["sensitive", "data"]
       }

       --

       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "pii_fields": ["sensitive", "data"]
       }

       --

       {
         "input_s3": "s3://ingestion_bucket/new_data/file1.csv",
         "output_s3": "",
         "pii_fields": ["sensitive", "data"]
       }
```

An input key must be provided, as must the field(s) to be obfuscated. The fields should be in a list, even if only one field is needed. The 'output' key is optional.

## AWS

As this tool is designed to be deployed on AWS Lambda, appropriate credentials are required. No credentials are stored inside the code, and should instead be supplied to the command line interface using `aws configure` or incorporated via environment variables before use.

AWS Lambda functions need appropriate permissions and IAM policies to interact with S3 Buckets. This lambda function requires S3:GetObject and S3:PutObject permission in order to stream files to and from S3. An example policy for a single bucket might look like this:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::your-test-bucket",
        "arn:aws:s3:::your-test-bucket/*"
      ]
    }
  ]
}
```

## Instructions

To view and interact with the source code, clone or fork this repo. Then, to run the code locally, write these commands into the terminal:

```
pip install -r requirements.txt
```

```
cd obfuscator-tool
```

```
python -c "from src.obfuscate import obfuscate_fields; print(obfuscate_fields('s3://bucket/input.csv', None, ['name']))"
```

(Replace the S3 URI and fields shown here with real data.)

The deployment code is located in the downloadable `gdpr-obfuscator-gh.zip` file shown in Assets on the Release page for this project. This file can be uploaded directly to AWS Lambda and deployed in the AWS console, subject to credentials and permissions.

## Running Tests

This project is unit tested with `monkeypatch` and `moto`. To run the test suite, please use Pytest:

```
pytest -v
```

## Known Limitations & future improvements

- Expects CSVs to have header rows. If a headerless CSV is passed, the function will validate against expected field names and raise an error.

- Obfuscation token is fixed as \*\*\*\* (could be made configurable).

- Assumes UTF-8 CSVs processed with Python’s csv module (no special dialect/encoding handling by default).

- No built-in support for compressed CSVs (e.g., .gz) — possible future feature.

## Tech Stack

**Technologies used**

- Python
- AWS (Amazon Web Services)
- Boto3
- Moto
- smart_open
- Pytest

## License

[MIT](https://choosealicense.com/licenses/mit/)
