
import pandas as pd
import pyodbc
import progressbar
from tqdm import tqdm
from time import sleep

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
    SELECT  @@Servername AS ServerName , DB_NAME() AS DBName , isc.TABLE_Schema, isc.TABLE_NAME, isc.COLUMN_NAME, Data_Type , Numeric_Precision AS Prec , Numeric_Scale AS Scale , Character_Maximum_Length AS [Length] , COUNT(*) AS COUNT
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
    cols = []
    for key in dataframe.keys():
        cols.append(key)
    cols.append("Count_Not_Null")
    cols.append("Count_Null")
    dfUsageData = pd.DataFrame(columns=cols)
    # print dfUsageData
    # raw_input()
    # Progress Bar
    bar = progressbar.ProgressBar(maxval=len(dataframe), widgets=[progressbar.Percentage(), progressbar.Bar(marker=progressbar.AnimatedMarker())])
    bar.start()
    # for i in range(0,len(dataframe)):
    for i in range(0,len(dataframe)):
        row = dataframe.iloc[[i]]

        #Get Count of Not Nulls
        ctNOTNull = getCountofFieldNotNull(str(row["DBName"].values[0]),str(row["TABLE_Schema"].values[0]),str(row["TABLE_NAME"].values[0]), str(row["COLUMN_NAME"].values[0]), str(row["Data_Type"].values[0]))
        tempSeries = pd.Series(ctNOTNull, name = 'Count_Not_Null', index=[i])
        tempRow = pd.concat([row, tempSeries], axis = 1)

        #Get Count of Not Nulls and add to
        ctNull = getCountofFieldNull(str(row["DBName"].values[0]),str(row["TABLE_Schema"].values[0]),str(row["TABLE_NAME"].values[0]), str(row["COLUMN_NAME"].values[0]), str(row["Data_Type"].values[0]))
        tempSeries = pd.Series(ctNull, name = 'Count_Null', index=[i])
        tempRow = pd.concat([tempRow, tempSeries], axis = 1)

        # Add tempRow to output dfUsageData dataframe
        dfUsageData = dfUsageData.append(tempRow)

        bar.update(i)

    bar.finish()

    return dfUsageData


def getCountofFieldNotNull(db, schema, table, columnName, dataType):
    sql = ""
    # varchar, nvarchar
    if dataType == "varchar" or dataType == "nvarchar":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NOT NULL AND """ + "[" + columnName + "]" + """<> ''"""

    # int or decimal or money or bigint
    elif dataType == "int" or dataType == "decimal" or dataType == "money" or dataType == "bigint":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NOT NULL"""

    # text
    elif dataType == "text":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NOT NULL"""

    # datetime
    elif dataType == "datetime":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NOT NULL AND """ + "[" + columnName + "]" + """<> ''"""

    else:
        error = "Data Type " + str(dataType) + " Not Recognized"
        print(error)

    ct = pd.read_sql(sql, conn)
    return ct


def getCountofFieldNull(db, schema, table, columnName, dataType):
    sql = ""
    ## Handle different variable types for Null/Blank counting
    # varchar, nvarchar
    if dataType == "varchar" or dataType == "nvarchar":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NULL OR """ + "[" + columnName + "]" + """ = ''"""

    # int or decimal or money or bigint
    elif dataType == "int" or dataType == "decimal" or dataType == "money" or dataType == "bigint":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NULL"""

    # text
    elif dataType == "text":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NULL"""

    # datetime
    elif dataType == "datetime":
        sql = """SELECT COUNT(*)
            FROM """ +"[" + schema + "].[" + table + "]" + """
            WHERE """ + "[" + columnName + "]" + """ IS NULL OR """ + "[" + columnName + "]" + """ = ''"""
    else:
        error = "Data Type " + str(dataType) + " Not Recognized"
        raise(error)

    ct = pd.read_sql(sql, conn)
    return ct

tables = getTableInfo()
tables.to_csv('C:\Users\u672901\Desktop\\' + server + '_' + db + '_Table Info.csv')

colData = getColumnInfo_System()
usageData = getUsageData(colData)
usageData.to_csv('C:\Users\u672901\Desktop\\' + server + '_' + db + '_Usage Info.csv')

# dfColumns.to_csv('C:\Users\u672901\Desktop\TestExport.csv')
