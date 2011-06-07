from aggregation import Aggregator
from field_descriptor import FieldDescriptor
from query import QueryTokens
from twitter_fields import TwitterFields

class StatusSource(object):
    TWITTER_FILTER = 1
    TWITTER_SAMPLE = 2

class QueryOperator(object):
    """
        QueryOperator represents an operator in the stream query plan.
        Anyone who implements this class should implement the filter method,
        which takes a list of updates on the stream and returns the ones
        which match the filter.
    """
    def __init__(self):
        pass
    def filter(self, updates, return_passes, return_fails):
        raise  NotImplementedError()
    def filter_params(self):
        """
            Returns a tuple with lists: (follow_ids, track_words)
        """
        raise  NotImplementedError()
    def assign_descriptor(self, tuple_descriptor):
        raise NotImplementedError()
    def can_query_stream(self):
        return False
    def get_tuple_descriptor(self):
        return self.tuple_descriptor

class AllowAll(QueryOperator):
    """
        Allows all updates to pass this filter
    """
    def __init__(self):
        QueryOperator.__init__(self)
    def filter(self, updates, return_passes, return_fails):
        passes = updates
        for update in passes:
            update.set_tuple_descriptor(self.tuple_descriptor)
        fails = []
        if not return_passes:
            passes = None
        if not return_fails:
            fails = None
        return (passes, fails)
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor

class And(QueryOperator):
    """
        Logical AND between the operators that make up its children.
    """
    def __init__(self, children):
        QueryOperator.__init__(self)
        self.children = children
        self.can_query_stream_cache = self.can_query_stream_impl()
    def filter(self, updates, return_passes, return_fails):
        passes = updates
        fails = []
        for child in self.children:
            (passes, fails_local) = child.filter(passes, True, return_fails)
            if return_fails:
                fails.extend(fails_local)
        if not return_passes:
            passes = None
        if not return_fails:
            fails = None
        return (passes, fails)
    def filter_params(self):
        for child in self.children:
            if child.can_query_stream():
                return child.filter_params()
    def can_query_stream(self):
        return self.can_query_stream_cache
    def can_query_stream_impl(self):
        for child in self.children:
            if child.can_query_stream():
                return True
        return False
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor
        for child in self.children:
            child.assign_descriptor(tuple_descriptor)

class Or(QueryOperator):
    """
        Logical OR between the operators that make up its children.
    """
    def __init__(self, children):
        QueryOperator.__init__(self)
        self.children = children
        self.can_query_stream_cache = self.can_query_stream_impl()
    def filter(self, updates, return_passes, return_fails):
        passes = []
        fails = updates
        for child in self.children:
            (passes_local, fails) = child.filter(fails, return_passes, True)
            if return_passes:
                passes.extend(passes_local)
        if not return_passes:
            passes = None
        if not return_fails:
            fails = None
        return (passes, fails)
    def filter_params(self):
        (follow_ids, track_words) = ([], []) 
        for child in self.children:
            if child.can_query_stream():
                (follow_local, track_local) = child.filter_params()
                if follow_local != None:
                    follow_ids.extend(follow_local)
                if track_local != None:
                    track_words.extend(track_local)
        return (follow_ids, track_words)
    def can_query_stream(self):
        return self.can_query_stream_cache
    def can_query_stream_impl(self):
        for child in self.children:
            if not child.can_query_stream():
                return False
        return True
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor
        for child in self.children:
            child.assign_descriptor(tuple_descriptor)

class Not(QueryOperator):
    """
        Logical NOT on the child operator.
    """
    def __init__(self, child):
        QueryOperator.__init__(self)
        self.child = child
    def filter(self, updates, return_passes, return_fails):
        (passes, fails) = self.child.filter(updates, return_fails, return_passes)
        return (fails, passes)
    def filter_params(self):
        return self.child.filter_params()
    def can_query_stream(self):
        return self.child.can_query_stream()
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor
        self.child.assign_descriptor(tuple_descriptor)

class Follow(QueryOperator):
    """
        Passes updates which contain people in the follower list.
    """
    def __init__(self, ids):
        QueryOperator.__init__(self)
        self.ids = set(ids)
    def filter(self, updates, return_passes, return_fails):
        passes = [] if return_passes else None
        fails = [] if return_fails else None
        for update in updates:
            update.set_tuple_descriptor(self.tuple_descriptor)
            if update.author in self.ids:
                if return_passes:
                    passes.append(update.author)
            elif return_fails:
                fails.append(update.author)
        return (passes, fails)
    def filter_params(self):
        return (self.ids, None)
    def can_query_stream(self):
        return True 
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor

class Contains(QueryOperator):
    """
        Passes updates which contain the desired term.  Matching is case-insensitive.
    """
    def __init__(self, field_alias, term):
        QueryOperator.__init__(self)
        self.alias = field_alias
        self.term = term.lower()
    def filter(self, updates, return_passes, return_fails):
        passes = [] if return_passes else None
        fails = [] if return_fails else None
        for update in updates:
            update.set_tuple_descriptor(self.tuple_descriptor)
            if self.term in getattr(update, self.alias).lower():
                if return_passes:
                    passes.append(update)
            elif return_fails:
                fails.append(update)
        return (passes, fails)
    def filter_params(self):
        return (None, [self.term])
    def can_query_stream(self):
        if self.alias == TwitterFields.TEXT:
            return True
        else:
            return False
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor

class Equals(QueryOperator):
    """
        Passes updates which equal the desired term.  Matching is case-sensitive.
    """
    def __init__(self, field_alias, term):
        QueryOperator.__init__(self)
        self.alias = field_alias
        self.term = term
    def filter(self, updates, return_passes, return_fails):
        passes = [] if return_passes else None
        fails = [] if return_fails else None
        for update in updates:
            update.set_tuple_descriptor(self.tuple_descriptor)
            if self.term == getattr(update, self.alias):
                if return_passes:
                    passes.append(update)
            elif return_fails:
                fails.append(update)
        return (passes, fails)
    def filter_params(self):
        return (None, [self.term])
    def can_query_stream(self):
        if self.alias == TwitterFields.TEXT:
            return True
        else:
            return False
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor

class Location(QueryOperator):
    """
        Passes updates which are located in a geographic bounding box
    """
    def __init__(self, xmin, xmax, ymin, ymax):
        QueryOperator.__init__(self)
        (self.xmin, self.xmax, self.ymin, self.ymax) = (xmin, xmax, ymin, ymax)
    def filter(self, updates, return_passes, return_fails):
        passes = [] if return_passes else None
        fails = [] if return_fails else None
        for update in updates:
            update.set_tuple_descriptor(self.tuple_descriptor)
            x = update.geo.x
            y = update.geo.y
            if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
                if return_passes:
                    passes.append(update)
            elif return_fails:
                fails.append(update)
        return (passes, fails)
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor

class GroupBy(QueryOperator):
    """
        Groups results from child by some set of fields, and runs the aggregate 
        function(s) over them, emitting results and resetting buckets every
        window seconds.
    """
    def __init__(self, child, groupby, aggregates, window):
        QueryOperator.__init__(self)
        self.child = child
        self.can_query_stream_cache = self.can_query_stream_impl()
        self.groupby = groupby
        self.aggregates = aggregates
        self.window = window
        self.aggregator = Aggregator(self.aggregates, self.groupby, self.window)
    def filter(self, updates, return_passes, return_fails):
        if return_passes:
            (passes, fails) = self.child.filter(updates, return_passes, return_fails)
            new_emissions = []
            new_emissions.extend(self.aggregator.update(passes))
            return (new_emissions, None)
        else:
            return (None, None)
    def filter_params(self):
        return self.child.filter_params()
    def can_query_stream(self):
        return self.can_query_stream_cache
    def can_query_stream_impl(self):
        return self.child.can_query_stream()
    def assign_descriptor(self, tuple_descriptor):
        self.tuple_descriptor = tuple_descriptor
        self.aggregator.tuple_descriptor = tuple_descriptor
        with_aggregates = self.groupby.duplicate()
        for aggregate in self.aggregates:
            with_aggregates.add_descriptor(aggregate)
        with_aggregates.add_descriptor(TwitterFields.created_field)
        for alias, fd in tuple_descriptor.descriptors.items():
            with_aggregates.add_descriptor(fd)
        self.child.assign_descriptor(with_aggregates)
