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
    def can_query_stream(self):
        return False

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
                follow_ids.extend(follow_local)
                track_words.extend(track_local)
        return (follow_ids, track_ids)
    def can_query_stream(self):
        return self.can_query_stream_cache
    def can_query_stream_impl(self):
        for child in self.children:
            if not child.can_query_stream():
                return False
        return True

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
        return child.filter_params()
    def can_query_stream(self):
        return child.can_query_stream()

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

class Contains(QueryOperator):
    """
        Passes updates which contain the desired term
    """
    def __init__(self, term):
        QueryOperator.__init__(self)
        self.term = term.lower()
    def filter(self, updates, return_passes, return_fails):
        passes = [] if return_passes else None
        fails = [] if return_fails else None
        for update in updates:
            if self.term in update.text.lower():
                if return_passes:
                    passes.append(update)
            elif return_fails:
                fails.append(update)
        return (passes, fails)
    def filter_params(self):
        return (None, [self.term])
    def can_query_stream(self):
        return True

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
            x = update.geo.x
            y = update.geo.y
            if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
                if return_passes:
                    passes.append(update)
            elif return_fails:
                fails.append(update)
        return (passes, fails)
