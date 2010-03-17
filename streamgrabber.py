#!/usr/bin/env python

import getpass
import redis
import tweepy
import settings

class StreamGrabberListener(tweepy.StreamListener):
    """
    Manages tweets to be processed in redis.  Redis variables:
       - variable TWEET_GROUP_ID keeps track of the largest tweet group id issued yet
       - variable TO_INDEX is a list that stores the ids of tweet groups to be processed.
       - variables 'tweet-group:%d" are lists of tweets to be processed (tweet groups)
    """

    def __init__(self):
        tweepy.StreamListener.__init__(self)
        self.redis = redis.Redis(host=settings.REDIS_HOSTNAME, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.increment_tweet_group_id()
        
    def increment_tweet_group_id(self):
        self.tweet_group_id = self.redis.incr(settings.TWEET_GROUP_ID)
        self.tweet_group_listkey = 'tweet-group:%d' % (self.tweet_group_id)
        
    def on_data(self, data):
        """
        Push data into redis
        """
        if 'in_reply_to_status_id' in data:
            self.keep_or_update_tgid()
            self.insert_data(data)

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'
    
    def keep_or_update_tgid(self):
        if self.redis.llen(self.tweet_group_listkey) >= settings.MAX_MESSAGES:
            print 'done with %s' % (self.tweet_group_listkey)
            self.redis.lpush(settings.TO_INDEX, self.tweet_group_listkey)
            self.increment_tweet_group_id()
    
    def insert_data(self, data):
        self.redis.rpush(self.tweet_group_listkey, data)

def main():
    # Prompt for login credentials and setup stream object
    username = raw_input('Twitter username: ')
    password = getpass.getpass('Twitter password: ')
    stream = tweepy.Stream(username, password, StreamGrabberListener(), timeout=None)

    stream.sample()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
