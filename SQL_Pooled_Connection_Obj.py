import pyodbc

import sqlalchemy.pool as pool

import logging
logger = logging.getLogger()

class handler:
    def __init__(self, pool_size=1, max_overflow=10):
        self.pool = pool.QueuePool(self.connect, max_overflow=max_overflow, pool_size=pool_size)

    def connect(self):
        user = <user>
        pw = <password>
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=<server_IP_or_url>;DATABASE=<Database_Name>;UID=%s;PWD={%s};' %(user, pw))
        return conn

    def query(self, sql):
        conn = self.pool.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = cursor.description
        res = [dict(zip([column[0] for column in columns], row)) for row in cursor.fetchall()]
        conn.close()
        return res

    def execute(self, sql, try_count=1):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.commit()
            conn.close()
        except Exception as e:
            logger.debug(e)
            try_count += 1
            if try_count <= 3:
                self.execute(sql=sql, try_count=try_count)
            else:
                raise e


if __name__=="__main__":
    from tabulate import tabulate
    h = handler()
    sql = """SELECT * FROM Previous_WYF_Seeds_Int_Ext"""
    data = h.query(sql)
    print(tabulate(data[:100], headers='keys', tablefmt='psql'))
    pass
