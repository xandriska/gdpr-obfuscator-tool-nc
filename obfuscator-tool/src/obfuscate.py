"""

This function streams CSV files from - and back into - Amazon S3,
obfuscating values from relevant fields in the process.

The fields to obfuscate are supplied to the function by a JSON Lambda event.
To input these fields, please create a Lambda event with the shape described
in the README or lambda_handler.py, and replace the example fields in
"pii_fields" with the names of the fields you wish to obfuscate.

Please note: the fields to obfuscate must be in the form of a list,
even if only one field is needed.

"""

import csv

from smart_open import open as s3open


def obfuscate_fields(input_s3: str, output_s3: None,
                     fields_to_obfuscate: list, s3_client=None):

    # s3 URI extractor function

    def extract_s3_uri(uri):

        assert uri.startswith("s3://"), "s3 URI must start with s3://"

        parts = uri[5:].split("/", 1)

        bucket = parts[0]

        key = parts[1] if len(parts) > 1 else ""

        return bucket, key

    # create an output location/filename in case none is supplied
    if not output_s3:

        bucket, key = extract_s3_uri(input_s3)
        stem, ext = key.rsplit(".", 1)
        output_s3 = f"s3://{bucket}/{stem}_obfuscated.{ext}"

    # use smart open to stream the files as bytes directly from s3.
    with s3open(input_s3, "r",
                transport_params={"client": s3_client}) as fin, \
         s3open(output_s3, "w",
                transport_params={"client": s3_client}) as fout:

        reader = csv.DictReader(fin)
        headers = reader.fieldnames

        # an error is raised if the csv has no header row.
        if not headers:
            raise ValueError("No header row in input file.")

        # an error is raised if the requested fields aren't in input file.
        missing = [f for f in fields_to_obfuscate if f not in headers]

        if missing:

            raise ValueError(f"Fields not in CSV headers: {missing}")

        rows_processed = 0

        # store the output file with same headers as the input.
        writer = csv.writer(fout)
        writer.writerow(headers)

        # iterate over dictreader copy and obfuscate requested fields.
        for row in reader:
            out_row = row.copy()
            for field in fields_to_obfuscate:
                if field in out_row:
                    out_row[field] = "****"

            # write new values into file.
            writer.writerow([out_row.get(h, "") for h in headers])
            rows_processed += 1

    # create a result dictionary for the lambda handler.
    result = {
        "Status": "Success",
        "Input": input_s3,
        "Output": output_s3,
        "Fields obfuscated": fields_to_obfuscate,
        "Rows processed": rows_processed,
    }

    print(f"Processed {rows_processed} rows. Output written to {output_s3}.")
    return result
