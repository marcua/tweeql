from getpass import getpass
from ssql.exceptions import QueryException
from ssql.exceptions import DbException
from ssql.field_descriptor import ReturnType
from ssql.operators import StatusSource
from ssql.query_builder import gen_query_builder
from ssql.tuple_descriptor import Tuple
from sqlalchemy import create_engine, Table, Column, Integer, Unicode, Float, DateTime, MetaData
from threading import RLock
from threading import Thread
from tweepy import StreamListener
from tweepy import Stream

import settings

class QueryRunner(StreamListener):
    def __init__(self, status_handler, batch_size = 10000):
        StreamListener.__init__(self)
        try:
            username = settings.TWITTER_USERNAME
            password = settings.TWITTER_PASSWORD
        except AttributeError:
            print "TWITTER_USERNAME and TWITTER_PASSWORD not defined in settings"
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
    def run_built_query(self, query_built, async):
        self.query = query_built
        self.status_handler.set_tuple_descriptor(self.query.get_tuple_descriptor())
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
        query_str = unicode(query_str, 'utf-8')
        query_built = self.query_builder.build(query_str)
        self.run_built_query(query_built, async)
    def stop_query(self):
        self.stream.disconnect()
        self.flush_statuses()
    def filter_statuses(self, statuses, query, handler):
        (passes, fails) = query.query_tree.filter(statuses, True, False)
        handler.handle_statuses(passes)
    def flush_statuses(self):
        self.status_lock.acquire()
        if len(self.statuses) > 0:
            filter_func = lambda s=self.statuses, q=self.query, h=self.status_handler: self.filter_statuses(s,q,h)
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
        if len(self.statuses) >= self.batch_size:
            self.flush_statuses()
        self.status_lock.release()
    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True # keep stream alive
    def on_timeout(self):
        print 'Snoozing Zzzzzz'

class StatusHandler(object):
    def handle_statuses(self, statuses):
        raise NotImplementedError()
    def set_tuple_descriptor(self, descriptor):
        self.tuple_descriptor = descriptor

class PrintStatusHandler(StatusHandler):
    def __init__(self, delimiter = u"|"):
        self.delimiter = delimiter

    def handle_statuses(self, statuses):
        td = self.tuple_descriptor
        for status in statuses:
            vals = (unicode(val) for (alias, val) in status.as_iterable_visible_pairs())
            print self.delimiter.join(vals)

class DbInsertStatusHandler(StatusHandler):
    def __init__(self, tablename, dburi):
        self.dburi = dburi
        self.tablename = tablename

    def set_tuple_descriptor(self, descriptor):
        StatusHandler.set_tuple_descriptor(self, descriptor)
        self.engine = create_engine(self.dburi, echo=False)
        metadata = MetaData()
        columns = []
        for alias in descriptor.aliases:
            desc = descriptor.get_descriptor(alias)
            if desc.visible:
                columns.append(self.db_col(alias, descriptor))
        columns.insert(0, Column('__id', Integer, primary_key=True))
        self.table = Table(self.tablename, metadata, *columns)
        metadata.create_all(bind=self.engine)
        test = metadata.tables[self.tablename]
        self.verify_table()
   
    def db_col(self, alias, descriptor):
        return_type = descriptor.get_descriptor(alias).return_type
        type_val = None
        if return_type == ReturnType.INTEGER:
            type_val = Integer
        elif return_type == ReturnType.FLOAT:
            type_val = Float
        elif return_type == ReturnType.STRING:
            type_val = Unicode
        elif return_type == ReturnType.DATETIME:
            type_val = DateTime
        else:
            raise DbException("Unknown field return type: %s" % (return_type))
        return Column(alias, type_val)

    def verify_table(self):
        """
            Makes sure the table's schema is not different from the one in the database.
            This might happen if you try to load a query into a table which already
            exists and has a different schema.
        """
        metadata = MetaData()
        metadata.reflect(bind = self.engine)
        mine = str(self.table.columns)
        verified = str(metadata.tables[self.tablename].columns)
        if mine != verified:
            raise DbException("Table '%s' in the database has schema %s whereas the query's schema is %s" % (self.tablename, verified, mine)) 
 
    def handle_statuses(self, statuses):
        conn = self.engine.connect()
        dicts = [dict(status.as_iterable_visible_pairs()) for status in statuses]
        conn.execute(self.table.insert(), dicts)
        conn.close()
