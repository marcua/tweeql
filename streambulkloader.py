#!/usr/bin/env python

import csv
import psycopg2
import redis
import settings
import tempfile
import time

from tweepy.api import API
from tweepy.models import Status
from tweepy.utils import import_simplejson
from tweepy.utils import convert_to_utf8_str

api = API()
json = import_simplejson()

def bulk_load(listkey, tweets, db):
    with tempfile.NamedTemporaryFile(mode='w') as tmpfile:
        writer = csv.writer(tmpfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        print "list key '%s', file '%s'" % (listkey, tmpfile.name)
        for jsontweet in tweets:
            tweet = Status.parse(api, json.loads(jsontweet))
            retweeted = (getattr(tweet, 'retweeted_status', None) != None)
            writer.writerow([tweet.author.id, tweet.created_at, convert_to_utf8_str(tweet.text), retweeted])
            # TODO: geolocation
        tmpfile.flush()
        print "filled %s" % (tmpfile.name)
        copy_cmd = "COPY tweets (author_id, created_at, text, retweeted) FROM STDIN WITH DELIMITER AS ',' CSV QUOTE AS '\"'"
        cur = db.cursor()
        cur.copy_expert(copy_cmd, tmpfile)

def poll_data(r, db):
    listkey = r.rpoplpush(settings.TO_INDEX, settings.CONSUMED_INDICES)
    if listkey != None:
        tweets = r.lrange(listkey, 0, -1)
        bulk_load(listkey, tweets, db)
        r.lrem(settings.CONSUMED_INDICES, listkey, 0)
        r.delete(listkey)

def main():
    r = redis.Redis(host=settings.REDIS_HOSTNAME, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    conn_str = "dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME, settings.DATABASE_USERNAME, settings.DATABASE_HOST, settings.DATABASE_PASSWORD)
    db = psycopg2.connect(conn_str);
    while True:
        poll_data(r, db)
        time.sleep(settings.POLL_TIME)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
