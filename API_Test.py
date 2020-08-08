from bottle import run, get, post, request, delete
import pandas as pd
import MySQLdb


#SQL Parameters
server = 'localhost'
db = 'mydb'

#Create the connection
conn = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="dassowmd",         # your username
                     passwd="12345",  # your password
                     db="mydb")        # name of the data base

#animals = [{'name' : 'Ellie', 'type' : 'Elephant'},
#                        {'name' : 'Python', 'type' : 'Snake'},
#                        {'name' : 'Zed', 'type' : 'Zebra'}]

@get('/Speed_Test_Results')
def getAll():


        # you must create a Cursor object. It will let
        #  you execute all the queries you need
        cur = db.cursor()

        # Use all the SQL you like
        cur.execute("SELECT * FROM mydb.Internet_Speed_Test")

        # print all the first cell of all the rows
        results = {columns=}
        for row in cur.fetchall():
            print (row)

        return results

@get('/animal/<name>')
def getOne(name):
        the_animal = [animal for animal in animals if animal['name'] == name]
        return {'animal' : the_animal[0]}

@post('/Speed_Test_Results<Date_Test_Ran><Time_Test_Ran><IP_Address><User_Name><Ping_Time><Download_Time><Upload_Time>')
def addOne():
        new_animal = {'name' : request.json.get('name'), 'type' : request.json.get('type')}
        sql = """
        Insert INTO Internet_Speed_Test 
        VALUES (""" + Date_Test_Ran + """, """ + Time_Test_Ran + """, """ + IP_Address + """, """ + User_Name + """, """ + Ping_Time + """, """ + Download_Time + """, """ + Upload_Time + """)
        """
        conn.commit()
        return {'animals' : animals}

@delete('/animal/<name>')
def removeOne(name):
        the_animal = [animal for animal in animals if animal['name'] == name]
        animals.remove(the_animal[0])
        return {'animals' : animals}

run(reloader=True, debug=True)
