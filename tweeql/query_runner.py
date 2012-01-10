from getpass import getpass
from tweeql.builtin_functions import register_default_functions
from tweeql.exceptions import QueryException
from tweeql.exceptions import DbException
from tweeql.operators import StatusSource
from tweeql.query_builder import gen_query_builder
from tweeql.settings_loader import get_settings
from tweeql.tuple_descriptor import Tuple
from threading import RLock
from threading import Thread
from tweepy import Stream
from tweepy import StreamListener
from tweepy.auth import BasicAuthHandler

import time

settings = get_settings()

class QueryRunner(StreamListener):
    def __init__(self):
        register_default_functions()
        StreamListener.__init__(self)
        try:
            self.username = settings.TWITTER_USERNAME
            self.password = settings.TWITTER_PASSWORD
        except AttributeError:
            print "TWITTER_USERNAME and TWITTER_PASSWORD not defined in settings.py"
            self.username = raw_input('Twitter username: ')
            self.password = getpass('Twitter password: ')
        self.status_lock = RLock()
        self.statuses = []
        self.query_builder = gen_query_builder()
        self.stream = None
    def build_stream(self):
        if self.stream != None:
            self.stop_query()
            time.sleep(.01) # make sure old stream has time to disconnect
        self.stream = Stream(BasicAuthHandler(self.username, self.password),
                             self, # this object implements StreamListener
                             timeout = 600, # reconnect if no messages in 600s
                             retry_count = 20, # try reconnecting 20 times
                             retry_time = 10.0, # wait 10s if no HTTP 200
                             snooze_time = 1.0) # wait 1s if timeout in 600s
    def run_built_query(self, query_built, async):
        self.build_stream()
        self.query = query_built
        self.query.handler.set_tuple_descriptor(self.query.get_tuple_descriptor())
        if self.query.source == StatusSource.TWITTER_FILTER:
            no_filter_exception = QueryException("You haven't specified any filters that can query Twitter.  Perhaps you want to query TWITTER_SAMPLE?")
            try:
                (follow_ids, track_words) = self.query.query_tree.filter_params()
                if (follow_ids == None) and (track_words == [None]):
                    raise no_filter_exception
                self.stream.filter(follow_ids, track_words, async)
            except NotImplementedError:
                raise no_filter_exception
        elif self.query.source == StatusSource.TWITTER_SAMPLE:
            self.stream.sample(None, async)
    def run_query(self, query_str, async):
        if isinstance(query_str, str):
            query_str = unicode(query_str, 'utf-8')
        query_built = self.query_builder.build(query_str)
        self.run_built_query(query_built, async)
    def stop_query(self):
        if self.stream != None:
            self.stream.disconnect()
            self.flush_statuses()
    def filter_statuses(self, statuses, query):
        (passes, fails) = query.query_tree.filter(statuses, True, False)
        query.handler.handle_statuses(passes)
    def flush_statuses(self):
        self.status_lock.acquire()
        if len(self.statuses) > 0:
            filter_func = lambda s=self.statuses, q=self.query: self.filter_statuses(s,q)
            t = Thread(target = filter_func)
            t.start()
            self.statuses = []
        self.status_lock.release()

    """ StreamListener methods """
    def on_status(self, status):
        self.status_lock.acquire()
        t = Tuple()
        t.set_tuple_descriptor(None)
        t.set_data(status.__dict__)
        self.statuses.append(t)
        if len(self.statuses) >= self.query.handler.batch_size:
            self.flush_statuses()
        self.status_lock.release()
    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True # keep stream alive
    def on_timeout(self):
        print 'Snoozing Zzzzzz'
    def on_limit(self, limit_data):
        print "Twitter rate-limited this query.  Since query start, Twitter dropped %d messages." % (limit_data)
