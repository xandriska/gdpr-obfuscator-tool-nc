import boto3
from moto import mock_aws

from src.lambda_handler import lambda_handler


def test_lambda_success_if_output(monkeypatch):

    # arrange
    event = {
        "input_s3": "s3://test-bucket/input.csv",
        "output_s3": "s3://test-bucket/output.csv",
        "pii_fields": ["name", "email_address"],
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

    # arrange
    event = {"input_s3": "s3://test-bucket/input.csv",
             "pii_fields": ["name", "email"]}
    fake_result = {"status": "success"}

    def fake_obfuscate(input_s3, output_s3, fields, s3_client=None):
        if not output_s3:
            bucket, key = input_s3[5:].split("/", 1)
            stem, ext = key.rsplit(".", 1)
            output_s3 = f"s3://{bucket}/{stem}_obfuscated.{ext}"
        assert output_s3 == "s3://test-bucket/input_obfuscated.csv"
        return fake_result

    monkeypatch.setattr("src.lambda_handler.obfuscate_fields", fake_obfuscate)

    # act

    result = lambda_handler(event, None)

    # assert
    assert result == fake_result


def test_lambda_handler_error_no_input():

    # arrange
    event = {"output_s3": "s3://bucket/output.csv", "pii_fields": ["name"]}

    # act
    result = lambda_handler(event, None)

    # assert
    assert result["status"] == "error"
    assert "'input_s3' key is required" in result["message"]


def test_lambda_handler_missing_fields():

    # arrange
    event = {
        "input_s3": "s3://bucket/input.csv",
        "output_s3": "s3://bucket/output.csv",
    }

    # act
    result = lambda_handler(event, None)

    # assert
    assert result["status"] == "error"
    assert "'pii_fields' key is required" in result["message"]


@mock_aws
def test_lambda_handler_with_moto_no_output():

    # arrange
    s3 = boto3.client("s3")
    location = {"LocationConstraint": "eu-west-2"}
    s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration=location)

    test_body = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

    s3.put_object(Bucket="test-bucket", Key="input.csv", Body=test_body)

    event = {"input_s3": "s3://test-bucket/input.csv",
             "pii_fields": ["Customer"]}

    # act
    result = lambda_handler(event, None)

    # assert
    assert result["status"] == "success"
    assert result["rows processed"] == 4
    assert result["output"] == "s3://test-bucket/input_obfuscated.csv"

    response = s3.get_object(Bucket="test-bucket", Key="input_obfuscated.csv")
    content = response["Body"].read().decode("utf-8")

    assert "****" in content
    assert "Flavour" in content
    assert "Strawberry" in content


@mock_aws
def test_lambda_handler_with_moto_with_output():

    # arrange
    s3 = boto3.client("s3")
    location = {"LocationConstraint": "eu-west-2"}
    s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration=location)

    test_body = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

    s3.put_object(Bucket="test-bucket", Key="input.csv", Body=test_body)

    event = {
        "input_s3": "s3://test-bucket/input.csv",
        "output_s3": "s3://test-bucket/output.csv",
        "pii_fields": ["Customer"],
    }

    # act
    result = lambda_handler(event, None)

    # assert
    assert result["status"] == "success"
    assert result["rows processed"] == 4
    assert result["output"] == "s3://test-bucket/output.csv"

    response = s3.get_object(Bucket="test-bucket", Key="output.csv")
    content = response["Body"].read().decode("utf-8")

    assert "****" in content
    assert "Flavour" in content
    assert "Strawberry" in content
