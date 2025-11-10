import csv
import io
import pytest
import boto3
from moto import mock_aws

import src.obfuscate
from src.obfuscate import obfuscate_fields

# -------- non-closing file wrapper ------------ #


class NonClosingStringIO:

    def __init__(self, real_buffer):
        self.buffer = real_buffer

    def write(self, data):
        return self.buffer.write(data)

    def read(self, *args, **kwargs):
        return self.buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self.buffer.seek(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self):
        pass


# ---------------------------------------------- #


def test_obfuscate_opens_csv(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer", "Size"]

    def fake_open(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if uri == "s3://test-bucket/input.csv" and mode == "r":
            return io.StringIO(fake_csv)
        elif uri == "s3://test-bucket/output.csv" and mode == "w":
            return io.StringIO()

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open)

    # act

    result = obfuscate_fields(test_input, test_output,
                              test_fields, s3_client=None)

    # assert

    assert result["Rows processed"] == 4


@mock_aws
def test_obfuscate_reads_writes_from_s3():

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer", "Size"]

    test_client = boto3.client("s3")

    location = {"LocationConstraint": "eu-west-2"}

    test_bucket = "test-bucket"

    test_client.create_bucket(Bucket=test_bucket,
                              CreateBucketConfiguration=location)

    input_key = "input.csv"

    output_key = "output.csv"

    fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

    test_client.put_object(Bucket=test_bucket, Key=input_key, Body=fake_csv)

    # act

    obfuscate_fields(test_input, test_output,
                     test_fields, s3_client=test_client)

    # assert

    response = test_client.get_object(Bucket=test_bucket, Key=output_key)

    output_csv = response["Body"].read().decode("utf-8")

    assert output_csv != fake_csv


def test_obfuscate_writes_file_with_same_headers(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer", "Size"]

    test_output_dict = {}

    expected_headers = ["Customer", "Flavour", "Size", "Price"]

    def fake_open2(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open2)

    # act

    obfuscate_fields(test_input, test_output,
                     test_fields, s3_client=None)

    buffer = test_output_dict[test_output]

    buffer.seek(0)

    test_written_file = buffer.read()

    lines = test_written_file.splitlines()

    header_row = lines[0].split(",")

    # assert

    assert header_row == expected_headers


def test_obfuscate_replaces_single_fields(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer"]

    test_output_dict = {}

    def fake_open3(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open3)

    # act

    obfuscate_fields(test_input, test_output,
                     test_fields, s3_client=None)

    buffer = test_output_dict[test_output]

    buffer.seek(0)

    test_output_file = buffer.read()

    f = io.StringIO(test_output_file)
    test_output_lst_dcts = list(csv.DictReader(f))

    for dct in test_output_lst_dcts:
        assert dct["Customer"] == "****"


def test_obfuscate_replaces_multiple_fields(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer", "Size", "Price"]

    test_output_dict = {}

    def fake_open4(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open4)

    # act

    obfuscate_fields(test_input, test_output,
                     test_fields, s3_client=None)

    buffer = test_output_dict[test_output]

    buffer.seek(0)

    test_output_file = buffer.read()

    f = io.StringIO(test_output_file)
    test_output_lst_dcts = list(csv.DictReader(f))

    for dct in test_output_lst_dcts:
        assert dct["Customer"] == "****"
        assert dct["Size"] == "****"
        assert dct["Price"] == "****"


def test_error_raised_if_csv_empty(monkeypatch):

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Customer", "Size", "Price"]

    test_output_dict = {}

    def fake_open4(uri, mode="r", transport_params=None):

        fake_csv = ""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open4)

    # act

    with pytest.raises(ValueError):

        obfuscate_fields(test_input, test_output, test_fields, s3_client=None)


def test_error_raised_if_wrong_fields(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_output = "s3://test-bucket/output.csv"

    test_fields = ["Name", "Email", "Phone"]

    test_output_dict = {}

    def fake_open5(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open5)

    # act

    with pytest.raises(ValueError) as excinfo:

        obfuscate_fields(test_input, test_output, test_fields, s3_client=None)

    message = str(excinfo.value)

    # assert

    assert "Fields not in CSV headers:" in message
    assert "Name" in message
    assert "Email" in message


def test_obfuscate_creates_output_path_if_none(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_fields = ["Customer", "Size"]

    test_output_dict = {}

    def fake_open5(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open5)

    # act

    result = obfuscate_fields(test_input, None, test_fields, s3_client=None)

    # assert

    assert result["Output"] == "s3://test-bucket/input_obfuscated.csv"


def test_obfuscate_creates_output_path_if_empty(monkeypatch):

    # arrange

    test_input = "s3://test-bucket/input.csv"

    test_fields = ["Customer", "Size"]

    test_output = ""

    test_output_dict = {}

    def fake_open6(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open6)

    # act

    result = obfuscate_fields(test_input, test_output,
                              test_fields, s3_client=None)

    # assert

    assert result["Output"] == "s3://test-bucket/input_obfuscated.csv"


def test_obfuscate_rejects_bad_uri(monkeypatch):

    test_input = "s3:/test-bucket/input.csv"

    test_output = ""

    test_fields = ["Customer", "Size"]

    test_output_dict = {}

    def fake_open7(uri, mode="r", transport_params=None):

        fake_csv = """Customer,Flavour,Size,Price
        Alice,Chocolate,Large,3.50
        Bob,Vanilla,Small,1.80
        Charlie,Strawberry,Medium,2.50
        Diana,Mint Choc Chip,Large,3.70"""

        if mode == "r":
            return io.StringIO(fake_csv)
        elif mode == "w":
            buffer = io.StringIO()
            test_output_dict[uri] = buffer
            return NonClosingStringIO(buffer)

    monkeypatch.setattr(src.obfuscate, "s3open", fake_open7)

    # act

    # assert

    with pytest.raises(AssertionError):
        obfuscate_fields(test_input, test_output,
                         test_fields, s3_client=None)
