import pandas as pd
import pyodbc
import progressbar
from tqdm import tqdm


# Parameters
# server = raw_input('What server would you like to connect to?\n')
# db = raw_input('What database would you like to research?\n')
# # Create the connection
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + db + ';Trusted_Connection=yes')

def testSearch():
    sql = """select *
    from openquery(DB2Test,
    'Select *
    FROM
    TC051001
    ')"""

    dfTables = pd.read_sql(sql, conn)
    return dfTables


res = testSearch()
print res.head()