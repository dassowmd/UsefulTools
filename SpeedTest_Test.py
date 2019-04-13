import pandas as pd
import pyodbc

import MySQLdb

conn = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="dassowmd",         # your username
                     passwd="12345",  # your password
                     db="mydb")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = conn.cursor()

# Use all the SQL you like
cur.execute("SELECT * FROM mydb.Internet_Speed_Test")

# print all the first cell of all the rows
results = {}
for row in cur.fetchall():
    print row
    tempDict = dict.fromkeys(row)
    results.update(tempDict)

print results

conn.close()

