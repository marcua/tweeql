#!/usr/bin/env python

import settings
import csv
import redis
import tempfile
import time

from tweepy.api import API
from tweepy.models import Status
from tweepy.utils import import_simplejson
from tweepy.utils import convert_to_utf8_str

api = API()
json = import_simplejson()

def bulk_load(listkey, tweets):
    with tempfile.NamedTemporaryFile(mode='w') as tmpfile:
        writer = csv.writer(tmpfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        print "list key '%s', file '%s'" % (listkey, tmpfile.name)
        for jsontweet in tweets:
            tweet = Status.parse(api, json.loads(jsontweet))
            retweeted = (getattr(tweet, 'retweeted_status', None) != None)
            writer.writerow([tweet.author.screen_name, tweet.created_at, convert_to_utf8_str(tweet.text), retweeted])
            # TODO: geolocation
        tmpfile.flush()
        copy_cmd = "COPY tweets ( screen_name, created_at, text, retweeted ) FROM '%s' WITH DELIMITER AS ',' CSV QUOTE AS '\"'"
        copy_cmd = copy_cmd % (tmpfile.name)

def poll_data(r):
    listkey = r.rpoplpush(settings.TO_INDEX, settings.CONSUMED_INDICES)
    if listkey != None:
        tweets = r.lrange(listkey, 0, -1)
        bulk_load(listkey, tweets)
        r.lrem(settings.CONSUMED_INDICES, listkey, 0)
        r.delete(listkey)

def main():
    r = redis.Redis(host=settings.REDIS_HOSTNAME, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    while True:
        poll_data(r)
        time.sleep(settings.POLL_TIME)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
