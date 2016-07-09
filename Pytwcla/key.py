#!/usr/bin/env python
"""Create and manipulate databases of Tweets matching a specified keyword."""

import sys
import os.path
import time
import datetime
import sqlite3
import csv
import tweepy
try:
    import ConfigParser
except:
    import configparser

def _path_finder(fol,fil):
    (head,tail) = os.path.split(__file__)
    path = os.path.join(head,fol,fil)
    return (path)

class query(object):

    def __init__(self, keyword):
        self.keyword = keyword
  
    @staticmethod    
    def __api_init():
        config = ConfigParser.ConfigParser()
        config.read(_path_finder('userconfig','api.ini'))
        consumer_key = config.get('DEFAULT','ConsumerKey',0)
        consumer_secret = config.get('DEFAULT','ConsumerSecret',0)
        access_token = config.get('DEFAULT','AccessToken',0)
        access_token_secret = config.get('DEFAULT','AccessTokenSecret',0)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, 
                         wait_on_rate_limit_notify=True)
        if (not api):
            print("Can't Authenticate.")
            sys.exit(-1)
        return (api)
        
    def __db_init(self, type):
        self.conn = sqlite3.connect(_path_finder(
                            'keydata','{0}_{1}.db'.format(self.keyword, type)),
                                                        check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS tweets
                          (id INT PRIMARY KEY ASC, date TEXT)''')
        return (self.conn, self.c)
            
    def rest_api(self):
        """
        Return and store tweets using Twitter's REST API.
        
        Returns:
            sqlite database file: [keyword]_rest.db
        """
        self.__db_init('rest')
        api = self.__api_init()
        self.c.execute("SELECT MAX(id) FROM tweets")
        db_max_id = self.c.fetchone()[0]        
        try: 
            most_recent = api.search(q=self.keyword, result_type='recent')[0].id
        except tweepy.TweepError as e:
            print(str(e.message[0]['message']) + 
                                ' Update api.ini with your proper credentials:')
            print(os.path.abspath(_path_finder('UserConfig','api.ini')))
            sys.exit(-1)
        flag = 0
        while ( flag == 0 ):
            try:
                batch = 5000
                flag = batch
                for search_res in tweepy.Cursor(api.search, q=self.keyword,
                                               count=100, result_type="recent", 
                                               since_id=db_max_id, 
                                               max_id=most_recent).items(batch):
                    flag -= 1
                    print(search_res.id, search_res.created_at)
                    self.c.execute('''INSERT OR IGNORE INTO tweets (id, date) 
                                      VALUES (?, ?)''', 
                                      (search_res.id, search_res.created_at))
            except tweepy.TweepError as e:
                print('I caught an error:', e.message)
                flag = 0
            finally:
                self.c.execute("SELECT last_insert_rowid() from tweets")
                rid = self.c.fetchone()[0]
                if rid:
                    self.c.execute('''SELECT id FROM tweets WHERE
                                      rowid={0}'''.format(rid))
                    rid = self.c.fetchone()[0]
                    most_recent = rid - 1
        data = api.rate_limit_status()
        print(data['resources']['search'])
        self.conn.commit()
        self.conn.close()
        print('REST database file has been created/updated:')        
        print(os.path.abspath(_path_finder(
                                'keydata','{0}_rest.db'.format(self.keyword))))
                
    def stream_api(self):
        """
        Return and store tweets using Twitter's Streaming API.
        
        Returns:
            sqlite database file: [keyword]_stream.db
        """
        (conn, c) = self.__db_init('stream')
        api = self.__api_init()

        class MyStreamListener(tweepy.StreamListener):
            
            def __init__(self, api=None):
                self.api = api
            
            def on_status(self, status):
                print(status.id, status.created_at)
                c.execute('''INSERT OR IGNORE INTO tweets (id, date) 
                             VALUES (?, ?)''' , (status.id, status.created_at))
                conn.commit()
            
            def on_error(self, status_code):
                if status_code == 401:
                    print('Bad Authentication data.' + 
                                ' Update api.ini with your proper credentials:')
                    print(os.path.abspath(
                                        _path_finder('UserConfig','api.ini')))
                    return False #Disconnect the stream.
                elif status_code == 420:
                    print('Error 420')
                    return False #Disconnect the stream.
                else:
                    print('Got an error with status code:', str(status_code))
                    time.sleep(321)
                    return True #Continue listening.

        print('Press Ctrl+C to exit stream')
        myStream = tweepy.Stream(auth = api.auth, 
                                listener = MyStreamListener()) #Create Stream
        myStream.filter(track=[self.keyword], async=False) #Start Stream
                        
    def merge_db(self):
        """
        Merge rest and stream database files to improve completeness of data.
        
        Returns:
            sqlite database file: [keyword]_joined.db              
        """
        path_1 = _path_finder('keydata','{0}_rest.db'.format(self.keyword))
        path_2 = _path_finder('keydata','{0}_stream.db'.format(self.keyword))
        if os.path.isfile(path_1) & os.path.isfile(path_2):
            self.__db_init('joined')
            self.c.execute("ATTACH '{0}' as restdb".format(path_1))
            self.c.execute("ATTACH '{0}' as streamdb".format(path_2))
            self.c.execute('''INSERT OR IGNORE INTO main.tweets(id,date) 
                            SELECT * FROM restdb.tweets 
                            UNION 
                            SELECT * FROM streamdb.tweets''')
            self.c.execute("DETACH DATABASE 'restdb'")
            self.c.execute("DETACH DATABASE 'streamdb'")
            self.conn.commit()
            self.conn.close()
            print('Databases have been merged:')
            print(os.path.abspath(_path_finder(
                            'keydata','{0}_joined.db'.format(self.keyword))))
            
    def create_csv(self, type):
        """
        Generate csv file with daily keyword statistics from the associated
        database file.
        
        Args:
            type (str): Valid values include: 'rest', 'stream', 'joined'.
        Returns:
            csv file: [keyword]_[type].csv (based on data from 
            [keyword]_[type].db)
        """        
        if os.path.isfile(_path_finder('keydata','{0}_{1}.db'.format(
                                                        self.keyword,type))):
            self.__db_init('{0}'.format(type))
            self.c.execute("SELECT MIN(date) FROM tweets")
            mindate = self.c.fetchone()[0][0:10]
            self.c.execute("SELECT MAX(date) FROM tweets")
            maxdate = self.c.fetchone()[0][0:10]
            start_date = datetime.datetime.strptime(mindate, '%Y-%m-%d')
            end_date = (datetime.datetime.strptime(maxdate, '%Y-%m-%d') + 
                        datetime.timedelta(days=1))
        
            def __date_range(start, end):
                for n in range((end - start).days):
                    yield start + datetime.timedelta(days=n)
        
            def __db_to_list():
                for single_date in __date_range(start_date, end_date):
                    d = "".join(['%',single_date.strftime("%Y-%m-%d"),'%'])
                    self.c.execute('''SELECT count(*) FROM tweets where 
                                    date like('{0}')'''.format(d))
                    yield [d[1:11], self.c.fetchone()[0]]
            
            path = _path_finder('keydata','{0}_{1}.csv'.format(
                                                            self.keyword,type))
            with open(path, 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(__db_to_list())
            self.conn.commit()
            self.conn.close()
            print('Report has been created:')
            print(os.path.abspath(path))