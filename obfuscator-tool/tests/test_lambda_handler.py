import boto3
import moto
import pytest

from src.lambda_handler import lambda_handler


def test_lambda_success_if_output(monkeypatch):

    # arrange 
    event = {
        "input_s3": "s3://test-bucket/input.csv",
        "output_s3": "s3://test-bucket/output.csv",
        "pii_fields": ["name", "email_address"]
    }

    expected_result = {"status": "success"}

    def fake_obfuscate(input_s3, output_s3, fields, s3_client=None):
        assert input_s3 == event["input_s3"]
        assert output_s3 == event["output_s3"]
        assert fields == event["pii_fields"]
        return expected_result

    monkeypatch.setattr("src.lambda_handler.obfuscate_fields", fake_obfuscate)

    # act

    result = lambda_handler(event, None)

    # assert
    assert result == expected_result


def test_lambda_success_if_no_output(monkeypatch):
    event = {
        "input_s3": "s3://test-bucket/input.csv",
        "pii_fields": ["name", "email"]
    }
    fake_result = {"status": "success"}

    def fake_obfuscate(input_s3, output_s3, fields, s3_client=None):
        if not output_s3:
            bucket, key = input_s3[5:].split('/', 1)
            stem, ext = key.rsplit('.', 1)
            output_s3 = f"s3://{bucket}/{stem}_obfuscated.{ext}"
        assert output_s3 == "s3://test-bucket/input_obfuscated.csv"
        return fake_result

    monkeypatch.setattr("src.lambda_handler.obfuscate_fields", fake_obfuscate)

    result = lambda_handler(event, None)
    assert result == fake_result

