class Aggregator():
    def __init__(self, aggregates, groupby):
        self.aggregates = aggregates
        self.groupby = groupby
        self.buckets = {}
    def update(self, updates):
        for update in updates:
            bucket = update.generate_from_descriptor(groupby)
            
            get agg field desc
            create aggregate tuples
            update tuples
            if update not in self.buckets:
                aggs = []
                for aggregate in self.aggregates:
                    factory = aggregate.aggregate_factory
                    underlying = aggregate.underlying_fields
                    aggs.append(factory.create(underlying_fields))
                self.buckets[update] = aggs
            for aggregate in self.buckets[update]:
                aggregate.update(tuple)
            # TODO: window?

class Aggregate():
    def __init__(self, underlying_fields):
        self.underlying_fields = underlying_fields
        self.reset()
    def update(self, tuple):
        raise  NotImplementedError()
    def value(self):
        raise NotImplementedError()
    def reset(self):
        raise NotImplementedError()


class Avg(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Avg(underlying_fields)
    def update(self, tuple):
        self.sum += getattr(tuple, self.underlying_fields[0])
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
    def update(self, tuple):
        self.count += 1
    def value(self):
        return self.count
    def reset(self):
        self.count = 0

class Sum(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Sum(underlying_fields)
    def update(self, tuple):
        self.sum += getattr(tuple, self.underlying_fields[0])
    def value(self):
        return self.sum
    def reset(self):
        self.sum = 0

class Min(Aggregate):
    @classmethod
    def create(cls, underlying_fields):
        return Min(underlying_fields)
    def update(self, tuple):
        val = getattr(tuple, self.underlying_fields[0])
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
    def update(self, tuple):
        val = getattr(tuple, self.underlying_fields[0])
        if (self.max is None) or (val > self.max):
            self.max = val
    def value(self):
        return self.max
    def reset(self):
        self.max = None
