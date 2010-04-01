#!/usr/bin/env python

import csv
import os
import sys
import psycopg2
import psycopg2.extensions
import redis
import settings
import tempfile
import time

from tweepy.api import API
from tweepy.utils import convert_to_utf8_str
from tweepy.utils import import_simplejson
from tweepy.models import Status

api = API()
json = import_simplejson()

def gen_tuple(jsontweet):
    tweet = Status.parse(api, json.loads(jsontweet))
    retweeted = (getattr(tweet, 'retweeted_status', None) != None)
    return (tweet.author.id, tweet.created_at, convert_to_utf8_str(tweet.text), retweeted)
    
def bulk_load(listkey, tweets, db):
    print "bulk-loading %d tweets from '%s'" % (len(tweets), listkey)
    insert_cmd = "INSERT INTO tweets (author_id, created_at, tweet, retweeted) VALUES (%s, %s, %s, %s);"
    cur = db.cursor()
    cur.executemany(insert_cmd, (gen_tuple(jsontweet) for jsontweet in tweets))
    db.commit()

def poll_data(r, db):
    listkey = r.rpoplpush(settings.TO_INDEX, settings.CONSUMED_INDICES)
    if listkey != None:
        tweets = r.lrange(listkey, 0, -1)
        bulk_load(listkey, tweets, db)
        r.lrem(settings.CONSUMED_INDICES, listkey, 0)
        r.delete(listkey)

def main():
    r = redis.Redis(host=settings.REDIS_HOSTNAME, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    conn_str = "dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_HOST, settings.DATABASE_PASSWORD)
    db = psycopg2.connect(conn_str);
    db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
    while True:
        poll_data(r, db)
        time.sleep(settings.POLL_TIME)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
