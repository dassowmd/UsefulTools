
import pandas as pd
import pyodbc
import progressbar
from tqdm import tqdm
from time import sleep
from tabulate import tabulate

# Parameters
server = raw_input('What server would you like to connect to?\n')
db = raw_input('What database would you like to research?\n')
# Create the connection
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + db + ';Trusted_Connection=yes')

# Get Tables in Database and Row Counts in Each
def getTableInfo():
    sql = """
    	SELECT  @@ServerName AS Server ,
            DB_NAME() AS DBName ,
            OBJECT_SCHEMA_NAME(p.object_id) AS SchemaName ,
            OBJECT_NAME(p.object_id) AS TableName ,
            i.Type_Desc ,
            i.Name AS IndexUsedForCounts ,
            SUM(p.Rows) AS Rows
    FROM    sys.partitions p
            JOIN sys.indexes i ON i.object_id = p.object_id
                                  AND i.index_id = p.index_id
    WHERE   i.type_desc IN ( 'CLUSTERED', 'HEAP' )
                             -- This is key (1 index per table)
            AND OBJECT_SCHEMA_NAME(p.object_id) <> 'sys'
    GROUP BY p.object_id ,
            i.type_desc ,
            i.Name
    ORDER BY SchemaName ,
            TableName;
    """
    dfTables = pd.read_sql(sql, conn)
    return dfTables


def getColumnInfo_System():
    sql = """
    SELECT  @@Servername AS ServerName , DB_NAME() AS DBName , isc.TABLE_Schema, isc.TABLE_NAME, isc.COLUMN_NAME, Data_Type , Numeric_Precision AS Prec , Numeric_Scale AS Scale , Character_Maximum_Length AS [Length]
    FROM    information_schema.columns isc
            INNER JOIN information_schema.tables ist
                   ON isc.table_name = ist.table_name
    WHERE   Table_type = 'BASE TABLE'
    GROUP BY isc.TABLE_Schema,
            isc.TABLE_NAME,
            isc.COLUMN_NAME,
            Data_Type ,
            Numeric_Precision ,
            Numeric_Scale ,
            Character_Maximum_Length
    ORDER BY isc.TABLE_Schema,
            isc.TABLE_NAME,
            isc.COLUMN_NAME,
            Data_Type ,
            Numeric_Precision ,
            Numeric_Scale ,
            Character_Maximum_Length
    """
    dfColumns = pd.read_sql(sql, conn)
    # print dfColumns
    # print dfColumns[index=2]
    return dfColumns


def getUsageData(dataframe):
    dfUsageData_List = []
    for row in tqdm(dataframe.iterrows(), bar_format='percentage'):
        row = dict(row[1])
        # TODO Need to solve the data types issues before this will work and not error out

        #Get Total Count
        ct = getCount(str(row["DBName"]),str(row["TABLE_Schema"]),str(row["TABLE_NAME"]), str(row["COLUMN_NAME"]), str(row["Data_Type"]))
        row['Count_Total'] = ct

        #Get Count of Not Nulls
        ctNOTNull = getCountofFieldNotNull(str(row["DBName"]),str(row["TABLE_Schema"]),str(row["TABLE_NAME"]), str(row["COLUMN_NAME"]), str(row["Data_Type"]))
        row['Count_Not_Null'] = ctNOTNull

        #Get Count of Not Nulls and add to
        ctNull = getCountofFieldNull(str(row["DBName"]),str(row["TABLE_Schema"]),str(row["TABLE_NAME"]), str(row["COLUMN_NAME"]), str(row["Data_Type"]))
        row['Count_Null'] = ctNull

        # Add row to output dfUsageData list
        dfUsageData_List.append(row)


        # bar.update(i)

    # bar.finish()
    dfUsageData = pd.DataFrame(dfUsageData_List)
    return dfUsageData

def getCount(db, schema, table, columnName, dataType):
    try:
        sql = """SELECT COUNT(*) as Count
            FROM """ +"[" + schema + "].[" + table + "]"
        ct = pd.read_sql(sql, conn)
        return ct['Count'][0]

    except Exception as e:
        print e
        return None


def getCountofFieldNotNull(db, schema, table, columnName, dataType):
    try:
        sql = ""
        # varchar, nvarchar
        if dataType == "varchar" or dataType == "nvarchar":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NOT NULL AND """ + "[" + columnName + "]" + """<> ''"""

        # int or decimal or money or bigint
        elif dataType == "int" or dataType == "tinyint" or dataType == "decimal" or dataType == "money" or dataType == "bigint" or dataType == "float" or dataType == "smallint":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NOT NULL"""

        # text
        elif dataType == "text" or dataType == 'char' or dataType == 'nchar':
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NOT NULL"""

        # datetime
        elif dataType == "datetime" or dataType == "smalldatetime" or dataType == "date":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NOT NULL AND """ + "[" + columnName + "]" + """<> ''"""

        else:
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NOT NULL"""
        ct = pd.read_sql(sql, conn)
        return ct['Count'][0]
    except Exception as e:
        error = "Data Type " + str(dataType) + " Not Recognized"
        print(error)
        print e
        return None


def getCountofFieldNull(db, schema, table, columnName, dataType):
    try:
        sql = ""
        ## Handle different variable types for Null/Blank counting
        # varchar, nvarchar
        if dataType == "varchar" or dataType == "nvarchar":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NULL OR """ + "[" + columnName + "]" + """ = ''"""

        # int or decimal or money or bigint
        elif dataType == "int" or dataType == "tinyint" or dataType == "decimal" or dataType == "money" or dataType == "bigint" or dataType == "float" or dataType == "smallint":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NULL"""

        # text
        elif dataType == "text" or dataType == 'char':
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NULL"""

        # datetime
        elif dataType == "datetime" or dataType == "smalldatetime" or dataType == "date":
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NULL OR """ + "[" + columnName + "]" + """ = ''"""
        else:
            sql = """SELECT COUNT(*) as Count
                FROM """ +"[" + schema + "].[" + table + "]" + """
                WHERE """ + "[" + columnName + "]" + """ IS NULL"""

        ct = pd.read_sql(sql, conn)
        return ct['Count'][0]
    except Exception as e:
        print e
        error = "Data Type " + str(dataType) + " Not Recognized"
        print(error)
        return None

tables = getTableInfo()
tables.to_csv('C:\Users\u672901\Desktop\\' + server + '_' + db + '_Table Info.csv')

colData = getColumnInfo_System()
colData = getUsageData(colData)
colData.to_csv('C:\Users\u672901\Desktop\\' + server + '_' + db + '_Usage Info.csv')

# dfColumns.to_csv('C:\Users\u672901\Desktop\TestExport.csv')
