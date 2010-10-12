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
    with open('/home/marcua/data/tweets/%s' % (listkey), 'w') as tmpfile:
        print "file %s" % (tmpfile.name)
        for jsontweet in tweets:
            tweet = Status.parse(api, json.loads(jsontweet))
            tmpfile.write(convert_to_utf8_str(tweet.text) + "\n")

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
