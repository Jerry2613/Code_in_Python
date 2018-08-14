from bisect import bisect_left
from collections.abc import Sequence
from itertools import chain

class SortedSet(Sequence):

    def __init__(self, items=None ):
        self._items = sorted(set(items)) if items is not None else []
#        print(self._items)

    def __contains__(self, item):
        return item in self._items

    def __len__(self):
        return len(self._items)

    def __iter__(self):
#        return iter(self._items)
        for item in self._items:
            yield item

    def __getitem__(self, index):
#        print(index)
#        print(type(index))
#        return self._items[index]
        result = self._items[index]
        return SortedSet(result) if isinstance(index, slice) else result

    def __repr__(self):
        return "SortedSet({})".format(
            repr(self._items) if self._items else ''
        )

    def __eq__(self, rhs):
        if not isinstance(rhs, SortedSet):
            return NotImplemented
        return self._items == rhs._items

    def __ne__(self, rhs):
        if not isinstance(rhs, SortedSet):
            return NotImplemented
        return self._items != rhs._items

    def count(self, item):
        index = bisect_left(self._items, item)
        found = (index != len(self._items)) and (self._items[index] ==item)
        return int(found)

    def __add__(self, rhs):
        return SortedSet(chain(self._items, rhs._items))

    def __mul__(self, rhs):
        return self if rhs>0 else SortedSet()

    def __rmul__(self, lhs):
        return self * lhs