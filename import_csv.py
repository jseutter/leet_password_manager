#!/usr/bin/env python3

# This is for importing a keepassx csv file into an existing secrets file.
# If you want to create a new secrets file, use convert_csv.py instead.

import csv
from secrets import Secrets

secrets_file = 'junk.leet'
import_file = 'junk3.csv'
keyphrase = 'password'

# Read in data, store the headers line separately
headers = None
entries = []
with open(import_file, 'r') as f:
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

def entries_equal(a, b):
    return (a['title'] == b['title'] and 
        a['username'] == b['username'] and
        a['password'] == b['password'] and
        a['notes'] == b['notes'])

# Read in the existing secrets file, then look for duplicates.
s = Secrets(secrets_file, keyphrase)
s.read()
entries = s.entries()
dupe_count = 0
add_count = 0
for new_entry in new_entries:
    for entry in entries:
        if entries_equal(entry, new_entry):
            # Entry already exists, avoid adding a duplicate
            dupe_count += 1
            break
    else:
        # All secrets searched, no duplicates found.
        # Add to secrets.
        s.add_entry(new_entry)
        add_count += 1
s.write()

print('{} merged, {} entries, {} were duplicate, {} added as new'.format(
        import_file, len(new_entries), dupe_count, add_count))

