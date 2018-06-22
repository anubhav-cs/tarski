from typing import List, Set
from .. import errors as err


class Sort:
    """ A logical sort (aka type)
        Sorts are uniquely identified by their name (i.e. we don't allow two sorts with different characteristics
        but the same name). Hence, implementation-wise, we can hash and compare them based on name alone.
    """
    def __init__(self, name, language, builtin=False):
        self._name = name
        self.language = language
        self._domain = set()
        self.builtin = builtin

    def __str__(self):
        return 'Sort({})'.format(self.name)

    def __repr__(self):
        return self.name

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.language == other.language

    @property
    def name(self):
        return self._name

    def contains(self, x):
        # TODO - Refactor this, we shouldn't be checking for two different ways of representing a value
        try:
            return x.symbol in self._domain
        except AttributeError:
            return x in self._domain

    def cast(self, x):
        # TODO - Refactor this, we shouldn't be checking for two different ways of representing a value
        try:
            if x.symbol in self._domain:
                return x.symbol
        except AttributeError:
            if x in self._domain:
                return x
        return None

    def cardinality(self):
        return len(self._domain)

    def dump(self):
        return dict(name=self._name,
                    domain=list(self._domain))  # Copy the list

    def extend(self, constant):
        self._domain.add(constant.symbol)
        for p in parents(self):
            p.extend(constant)

    def domain(self):
        return (self.language.get_constant(v) for v in self._domain)


class Interval(Sort):
    def __init__(self, name, lang, encode_fn, lower_bound=None, upper_bound=None):
        super().__init__(name, lang)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.encode = encode_fn

    def is_within_bounds(self, x):
        """ Check whether a given value is within the bounds of the interval """
        if self.lower_bound is None or self.upper_bound is None:
            raise err.SemanticError("Attempted to check for belonging to Interval type with no bounds set yet")
        return self.lower_bound <= x <= self.upper_bound

    def set_bounds(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def extend(self, x):
        pass  # TODO ???

    def cast(self, x):
        if isinstance(x, str):
            try:
                return getattr(self, x)  # TODO: WHAT IS THIS??
            except AttributeError:
                pass
        y = self.encode(x)  # can raise ValueError
        if not self.is_within_bounds(y):
            raise ValueError("Interval.cast(): Symbol '{}' (encoded '{}') does not belong to the domain".format(x, y))
        return y

    def cardinality(self):
        return self.upper_bound - self.lower_bound + 1

    def contains(self, x, raises_exceptions=False):
        try:
            y = self.encode(x)
        except ValueError:
            if raises_exceptions:
                raise err.SemanticError('Cannot encode "{}"'.format(x))
            return False

        # Downcasting Python literals from their type to a subtype (i.e. Real
        # to Integer) works whenever the resulting instance of the subtype belongs
        # to the domain *and* Python equality over the subtype instance and the
        # supertype instance returns true. For instance, downcasting 1.0 to
        # integers is okay, but 1.2 will not.
        relevant_supers = set(parents(self))
        while len(relevant_supers) > 0:
            p = relevant_supers.pop()
            try:
                z = p.cast(x)
            except ValueError:
                raise err.LanguageError()
            if z is not None and y != z:
                if raises_exceptions:
                    raise err.SemanticError('{} casted into y: {} and z: {}, y!=z'.format(x, y, z))
                return False
            for p2 in parents(p):
                relevant_supers.add(p2)

        return self.is_within_bounds(y)

    def dump(self):
        return dict(name=self.name,
                    domain=[self.lower_bound, self.upper_bound])


def inclusion_closure(s: Sort) -> Set[Sort]:
    """ Calculates the inclusion closure over given sort s """
    closure = set()
    frontier = {s}
    while len(frontier) > 0:
        s = frontier.pop()
        closure.add(s)
        for p in parents(s):
            frontier.add(p)
    return closure


def parents(s: Sort) -> List[Sort]:
    """ Returns direct parent sorts in the sort hierarchy associated with
        the language
    """
    _parents = []
    for lhs, rhs in s.language.sort_hierarchy:
        if lhs == s.name:
            _parents.append(s.language.get_sort(rhs))
    return _parents


def children(s: Sort) -> List[Sort]:
    """ Return direct child sorts in the sort hierarchy associated with
        the language
    """
    _children = []
    for lhs, rhs in s.language.sort_hierarchy:
        if rhs == s:
            _children.append(s.language.sort(lhs))
    return _children


def int_encode_fn(x):
    return int(x)


def float_encode_fn(x):
    return float(x)


def build_the_naturals(lang):
    the_nats = Interval('Natural', lang, int_encode_fn, 0, 2 ** 32 - 1)
    the_nats.builtin = True
    return the_nats


def build_the_integers(lang):
    the_ints = Interval('Integer', lang, int_encode_fn, -(2 ** 31 - 1), 2 ** 31 - 1)
    the_ints.builtin = True
    return the_ints


def build_the_reals(lang):
    reals = Interval('Real', lang, float_encode_fn, -3.40282e+38, 3.40282e+38)
    reals.builtin = True
    # the_reals.pi = scipy.constants.pi
    return reals
