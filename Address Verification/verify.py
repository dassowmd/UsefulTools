# Usage
# python verify.py input.csv
# Available from https://dashboard.lob.com/#/verifications/create

import lob
import csv
import sys

lob.api_key = "test_88a07bc7c1185ad90ae4aba8695448013b2"

skipFirstLine = True

# Column indices in CSV
address1 = 3
address2 = 4
city = 6
state = 9
postcode = 8
country = 7

try:
    sys.argv[1]
except IndexError:
    print "Please provide an input CSV file as an argument."
    sys.exit()

# Open input files
inputFile = open(sys.argv[1], "rU")
csvInput = csv.reader(inputFile)

# Create output files
errors = open(
    "C:\\Users\\u672901\\Google Drive\\Python Library\\Address Verification\\errors.csv",
    "w",
)
verified = open(
    "C:\\Users\\u672901\\Google Drive\\Python Library\\Address Verification\\verified.csv",
    "w",
)

# Loop through input CSV rows
for idx, row in enumerate(csvInput):
    if skipFirstLine and idx == 0:
        continue

    # Sanity check
    sys.stdout.write(".")
    sys.stdout.flush()

    try:
        verifiedAddress = lob.Verification.create(
            address_line1=row[address1],
            address_line2=row[address2],
            address_city=row[city],
            address_state=row[state],
            address_zip=row[postcode],
            address_country=row[country],
        )
    except Exception, e:
        outputRow = ",".join(row) + "," + str(e) + "\n"
        errors.write(outputRow)
    else:
        # outputRow = verifiedAddress.address.address_line1 + ","
        # outputRow += verifiedAddress.address.address_line2 + ","
        # outputRow += verifiedAddress.address.address_city + ","
        # outputRow += verifiedAddress.address.address_state + ","
        # outputRow += verifiedAddress.address.address_zip + "\n"
        outputRow = ",".join(row) + "\n"
        verified.write(outputRow)

errors.close()
verified.close()
print "\n"
