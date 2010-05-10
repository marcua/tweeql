from getpass import getpass
from ssql.operators import StatusSource
from ssql.query_builder import gen_query_builder
from threading import RLock
from threading import Thread
from tweepy import StreamListener
from tweepy import Stream

class QueryRunner(StreamListener):
    def __init__(self, status_handler, batch_size = 10000):
        StreamListener.__init__(self)
        username = raw_input('Twitter username: ')
        password = getpass('Twitter password: ')
        self.status_lock = RLock()
        self.statuses = []
        self.batch_size = batch_size
        self.status_handler = status_handler
        self.query_builder = gen_query_builder()
        self.stream = Stream(username,
                             password,
                             self, # this object implements StreamListener
                             timeout = 600, # reconnect if no messages in 600s
                             retry_count = 20, # try reconnecting 20 times
                             retry_time = 10.0, # wait 10s if no HTTP 200
                             snooze_time = 1.0) # wait 1s if timeout in 600s
    def run_built_query(self, query_built):
        self.query = query_built
        # TODO: stop old query
        if self.query.source == StatusSource.TWITTER_FILTER:
            (follow_ids, track_words) = self.query.query_tree.filter_params()
            self.stream.filter(follow_ids, track_words, True)
        elif self.query.source == StatusSource.TWITTER_SAMPLE:
            self.stream.sample(None, True)
    def run_query(self, query_str):
        query_built = self.query_builder.build(query_str)
        self.run_built_query(query_built)
    def stop_query(self):
        self.stream.disconnect()
        self.flush_statuses()
    def filter_statuses(self, statuses, query, handler):
        (passes, fails) = query.query_tree.filter(statuses, True, False)
        handler.handle_statuses(passes)
    def flush_statuses(self):
        self.status_lock.acquire()
        filter_func = lambda: self.filter_statuses(self.statuses, self.query, self.status_handler)
        Thread(target = filter_func).start()
        self.statuses = []
        self.status_lock.release()

    """ StreamListener methods """
    def on_status(self, status):
        self.status_lock.acquire()
        self.statuses.append(status)
        if len(self.statuses) > self.batch_size:
            self.flush_statuses()
        self.status_lock.release()
    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True # keep stream alive
    def on_timeout(self):
        print 'Snoozing Zzzzzz'

class PrintStatusHandler(object):
    def handle_statuses(self, statuses):
        for status in statuses:
            print status.text
