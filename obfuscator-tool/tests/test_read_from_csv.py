import csv
import io

from src.utils.read_from_csv import process_csv

def test_input_file_has_():

    with open('obfuscator-tool/tests/students_with_scores.csv', newline='') as file:

        testfile = file.read()

        result = process_csv(testfile)

        for row in result:
            print(row)
        

        # assert isinstance(result, io.StringIO)

        # result.seek(0)

        # csv_reader = csv.DictReader(result)

        # assert len(list(csv_reader)) == 5

        # result.seek(0)

        # csv_reader = csv.DictReader(result)

        # assert csv_reader.fieldnames == ['student_id', 'student_name', 'score']
    
    