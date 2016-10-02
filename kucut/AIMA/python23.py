"""This module contains code that is standard in Python 2.3.
We include it for those who have not upgraded to 2.3 yet.
We've tested with 2.2, and 2.1 should also work."""

from __future__ import generators
import operator

try: bool
except:
    class bool(int):
        "Simple implementation of Booleans, as in PEP 285"
        def __init__(self, val): self.val = val
        def __int__(self): return self.val
        def __repr__(self): return ('False', 'True')[self.val]

    True, False = bool(1), bool(0)

try: sum
except:
    def sum(seq, start=0):
        """Sum the elements of seq.
        >>> sum([1, 2, 3])
        6
        """
        return reduce(operator.add, seq, start)

try: enumerate
except:
    def enumerate(collection):
        """Return an iterator that enumerates pairs of (i, c[i]). PEP 279.
        >>> list(enumerate('abc'))
        [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1
    
class Set:
    """This implements the Set class from PEP 218, except it does not
    overload the infix operators.  """
    
    def __init__(self, elements=[]):
        self.dict = {}
        for e in elements:
            self.dict[e] = 1

    def __contains__(self, element):
        return element in self.dict

    def __getitem__(self, i):
        return self.dict.items()[i]

    def add(self, element):
        self.dict[element] = 1
        
    def remove(self, element):
        del self.dict[element]

    def discard(self, element):
        if element in self.dict:
            del self.dict[element]
            
    def pop(self):
        key, val = self.dict.popitem()
        return key

    def clear(self):
        self.dict.clear()

    def union(self, other):
        return Set(self).union_update(other)

    def intersection(self, other):
        return Set(self).intersection_update(other)

    def union_update(self, other):
        for e in other:
            self.add(e)
        return self

    def intersection_update(self, other):
        for e in self.dict.keys():
            if e not in other:
                self.remove(e)
        return self

    def issubset(self, other):
        for e in self.dict.keys():
            if e not in other:
                return False
        return True

    def __iter__(self):
        for e in self.dict:
            yield e

    def __len__(self):
        return len(self.dict)

    def __cmp__(self, other):
        if self is other: return False
        if not isinstance(other, Set): return id(self) - id(other)
        return cmp(self.dict, other.dict)

    def __repr__(self):
        return "{%s}" % ", ".join([str(e) for e in self.dict.keys()])
