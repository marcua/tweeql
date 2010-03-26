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

class And(QueryOperator):
    """
        Logical AND between the operators that make up its children.
    """
    def __init__(self, children):
        QueryOperator.__init__(self)
        self.children = children
    def filter(self, updates, return_passes, return_fails):
        passes = updates
        fails = []
        for child in children:
            (passes_local, fails_local) = child.filter(passes, True, return_fails)
            if return_fails:
                fails.extend(fails_local)
        if not return_passes:
            passes = None
        if not return_fails:
            fails = None
        return (passes, fails)

class Or(QueryOperator):
    """
        Logical OR between the operators that make up its children.
    """
    def __init__(self, children):
        QueryOperator.__init__(self)
        self.children = children
    def filter(self, updates, return_passes, return_fails):
        passes = []
        fails = updates
        for child in children:
            (passes_local, fails) = child.filter(fails, return_passes, True)
            if return_passes:
                passes.extend(passes_local)
        if not return_passes:
            passes = None
        if not return_fails:
            fails = None
        return (passes, fails)

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
            else if return_fails:
                fails.append(update.author)
        return (passes, fails)

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
            if self.term in update.text.lower:
                if return_passes:
                    passes.append(update)
            else if return_fails:
                fails.append(update)
        return (passes, fails)

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
            else if return_fails:
                fails.append(update)
        return (passes, fails)
