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