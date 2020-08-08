import MySQLdb
import pandas
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

# Create the connection
conn = MySQLdb.connect(
    host="localhost",  # your host, usually localhost
    user="dassowmd",  # your username
    passwd="12345",  # your password
    db="mydb",
)  # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = conn.cursor()

ckey = "ursTpjsMmcyFiTEukgbbtMqNN"
csecret = "Wwrt0ox2tg7ql6pJQf3rIS8r09CBBCP0sk21klQMV9WVVqbfOM"
atoken = "708677102292217856-H6EWWIc4oitA8RDndiyAkGnsh9WpWQV"
asecret = "sy0f7lk7WmoOrjEkuaeuAZzuSANPLNB82O0ri2XQlgRtm"


def writeToDB(data):
    sql = (
        """INSERT INTO Twitter_Data (Time, username,                         search_Keyword, tweet) 
        VALUES ("""
        + data.time
        + """, ' """
        + data.screen_name
        + """', '"""
        + searchTerm
        + """', '"""
        + data.text
        + """')"""
    )
    # Use all the SQL you like
    cur.execute(sql)
    conn.commit()


class listener(StreamListener):
    def on_data(self, data):
        print "____________________"
        print (data)
        return True

    def on_error(self, status):
        print "Why is this happening?"
        print status


searchTerm = "election"
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=[searchTerm])


conn.close()
