# Documentation
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
# https://docs.sqlalchemy.org/en/13/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc
# https://docs.sqlalchemy.org/en/13/core/engines.html

import pandas as pd
import urllib
import sqlalchemy
from datetime import datetime

user = input('What user?')
pw = input('What is the password?')

params = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=18.213.233.196;DATABASE=Pioneer;UID=%s;PWD={%s};fast_executemany=True;' %(user, pw))
engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
conn = engine.connect()
df = pd.read_csv(r'C:\Users\mdassow\Downloads\ExcelExport.csv')
start_time = datetime.now()
df[:].to_sql(name='test', con=conn, if_exists='replace', chunksize=75, method='multi')
end_time = datetime.now()
print('run_time: %s' %(str(end_time - start_time)))
