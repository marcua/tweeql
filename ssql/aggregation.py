from ssql.query import QueryTokens 
from ssql.exceptions import QueryException

class Aggregator():
    def __init__(self, aggregates, groupby):
        self.aggregates = aggregates
        self.groupby = groupby
        self.tuple_descriptor
        self.buckets = {}
    def update(self, updates):
        for update in updates:
            bucket = update.generate_from_descriptor(groupby)
            if bucket not in self.buckets:
                aggs = []
                for aggregate in self.aggregates:
                    factory = aggregate.aggregate_factory
                    underlying = aggregate.underlying_fields
                    aggs.append(factory.create(underlying_fields))
                self.buckets[bucket] = aggs
            for aggregate in self.buckets[bucket]:
                aggregate.update(update)
            # TODO: window?

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
