#!/usr/bin/env python3

# This is for converting a keepassx csv file into our secrets format.
# If you want to import csv secrets into an already-existing secrets
# file, use import_csv.py instead.

import csv
from secrets import Secrets

in_file = 'junk.csv'
out_file = 'junk.leet'
keyphrase = 'password'

# Read in data, store the headers line separately
headers = None
entries = []
with open(in_file, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    first_row = True
    for row in reader:
        if first_row:
            headers = row
            first_row = False
            continue
        else:
            entries.append(row)

print(headers)


# Try to fit data into our data structure.  Our fields are:
#  id
#  title
#  username
#  password
#  notes
# Keepassx csv export has the fields:
#  Group
#  Title
#  Username
#  Password
#  URL
#  Notes
mapping = {  # Map csv fields to our fields
    'Group': None,
    'Title': 'title',
    'Username': 'username',
    'Password': 'password',
    'URL': 'url',
    'Notes': 'notes'
}

# Map csv fields to a column number in the source csv
mapping2 = {}
for k in mapping.keys():
    mapping2[k] = headers.index(k)

# Copy the data into our format
new_entries = []
for row in entries:
    new_entry = {}
    for k in mapping:
        if mapping[k] != None:
            new_entry[mapping[k]] = row[mapping2[k]]
    new_entries.append(new_entry)

print(new_entries)         

s = Secrets(out_file, keyphrase)
s.new_vault()
for entry in new_entries:
    s.add_entry(entry)
s.write()
print('{} read and exported to {}, {} entries'.format(in_file, out_file, len(new_entries)))
