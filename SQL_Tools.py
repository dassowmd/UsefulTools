import pandas as pd
import numpy as np
from multiprocessing.pool import ThreadPool


def SQL_Mass_Insert_df(df, table_name, conn, cursor):
    pool = ThreadPool(10)
    sql, record_list = generate_multiple_sql_insert_statement(df, table_name)
    count = 0
    while count <= len(record_list):
        temp_record_list = record_list[count : count + 1000]
        pool.apply_async(sql_insert_many, args=(sql, temp_record_list, conn, cursor))
        count += 1000
    pool.close()
    pool.join()


def sql_insert_many(sql, record_list, conn, cursor, try_count=1):
    try:
        try:
            cursor.executemany(sql, record_list)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            if try_count <= 3:
                try_count += 1
                sql_insert_many(
                    sql=sql,
                    record_list=record_list,
                    conn=conn,
                    cursor=cursor,
                    try_count=try_count,
                )
            else:
                print(e)
    except Exception as e:
        print("Error with connection in Load_Backups sql_insert: %s" % e)


def generate_multiple_sql_insert_statement(df, table):
    try:
        keys = "`"
        for key in df.keys():
            keys += str(key) + "`, `"
        insert_records = []
        for record in df.iterrows():
            record = record[1]
            insert_values = []
            for key, value in record.iteritems():
                if pd.isnull(value):
                    insert_values.append(None)
                elif type(value) == float or type(value) == type(np.float64):
                    insert_values.append(str(value))
                elif type(value) == str or type(value) == unicode:
                    insert_values.append(str(value.encode("utf8")))
                elif (
                    type(value) == int
                    or type(value) == long
                    or np.issubdtype(type(value), np.integer)
                ):
                    insert_values.append(str(value))
                elif type(value) == bool:
                    insert_values.append(str(value))
                else:
                    print("Data error")

            insert_values = tuple(insert_values)
            insert_records.append(insert_values)
            # remove last comma and space
        values = "%s, " * len(df.keys())
        values = values[:-2]
        keys = keys[:-3]
        sql = "INSERT INTO " + table + "(" + keys + ") VALUES (" + values + ");"
        return sql, insert_records
    except Exception as e:
        print(e)
