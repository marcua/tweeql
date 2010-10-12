from datetime import timedelta
from datetime import datetime
from tweeql.query import QueryTokens 
from tweeql.exceptions import QueryException
from threading import RLock

class Aggregator():
    def __init__(self, aggregates, groupby, windowsize):
        self.aggregates = aggregates
        self.groupby = groupby
        self.tuple_descriptor = None
        self.buckets = {}
        self.update_lock = RLock()
        kwargs = {windowsize[1]: int(windowsize[0])}
        self.windowsize = timedelta(**kwargs)
        self.window = None
        self.emptylist = []
    def update(self, updates):
        self.update_lock.acquire()
        output = self.emptylist
        for update in updates:
            if self.window == None:
                self.window = AggregateWindow(update.created_at, update.created_at + self.windowsize)
            # ignore all entries before the window
            test = self.window.windowtest(update.created_at)
            if test == AggregateWindowResult.AFTER:
                if output is self.emptylist:
                    output = []
                for bucket, aggs in self.buckets.items():
                    bucket.set_tuple_descriptor(self.tuple_descriptor)
                    for k,v in aggs.items():
                        setattr(bucket, k, v.value())
                    output.append(bucket)
                self.buckets = {}
                while self.window.windowtest(update.created_at) != AggregateWindowResult.IN:
                    self.window.advance(self.windowsize)
                test = AggregateWindowResult.IN
            if test == AggregateWindowResult.IN:
                bucket = update.generate_from_descriptor(self.groupby)
                if bucket not in self.buckets:
                    aggs = dict()
                    for aggregate in self.aggregates:
                        factory = aggregate.aggregate_factory
                        underlying = aggregate.underlying_fields
                        aggs[aggregate.alias] = factory(underlying)
                    self.buckets[bucket] = aggs
                for aggregate in self.buckets[bucket].values():
                    aggregate.update(update)
        self.update_lock.release()
        return output

class AggregateWindow():
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def windowtest(self, timeval):
        if timeval < self.start:
            return AggregateWindowResult.BEFORE
        if timeval < self.end:
            return AggregateWindowResult.IN
        return AggregateWindowResult.AFTER
    def advance(self, windowsize):
        self.start = self.end
        self.end = self.end + windowsize

class AggregateWindowResult():
    BEFORE = 1
    IN = 2
    AFTER = 3

class Aggregate():
    def __init__(self, underlying_fields):
        self.underlying_fields = underlying_fields
        self.reset()
    def update(self, t):
        raise  NotImplementedError()
    def value(self):
        raise NotImplementedError()
    def reset(self):
        raise NotImplementedError()

def get_aggregate_factory(agg_func):
    if agg_func == QueryTokens.AVG:
        return Avg.create
    elif agg_func == QueryTokens.COUNT:
        return Count.create
    elif agg_func == QueryTokens.SUM:
        return Sum.create
    elif agg_func == QueryTokens.MIN:
        return Min.create
    elif agg_func == QueryTokens.MAX:
        return Max.create
    else:
        return None

class Avg(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Avg(underlying_fields)
    def update(self, t):
        self.sum += getattr(t, self.underlying_fields[0])
        self.count += 1
    def value(self):
        return self.sum/self.count
    def reset(self):
        self.sum = 0
        self.count = 0

class Count(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Count(underlying_fields)
    def update(self, t):
        self.count += 1
    def value(self):
        return self.count
    def reset(self):
        self.count = 0

class Sum(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Sum(underlying_fields)
    def update(self, t):
        self.sum += getattr(t, self.underlying_fields[0])
    def value(self):
        return self.sum
    def reset(self):
        self.sum = 0

class Min(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Min(underlying_fields)
    def update(self, t):
        val = getattr(t, self.underlying_fields[0])
        if (self.min is None) or (val < self.min):
            self.min = val
    def value(self):
        return self.min
    def reset(self):
        self.min = None

class Max(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Max(underlying_fields)
    def update(self, t):
        val = getattr(t, self.underlying_fields[0])
        if (self.max is None) or (val > self.max):
            self.max = val
    def value(self):
        return self.max
    def reset(self):
        self.max = None
