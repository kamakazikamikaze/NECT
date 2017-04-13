from collections import defaultdict
from functools import wraps

def chunker(seq, size):
    """
    Break an iterable into n-size chunks

    See `Stack Overflow <http://stackoverflow.com/a/434328/1993468>`_ for more
    information.

    :param seq: Target iterable to go over
    :param int size: Number of values to include in each chunk
    :return: Sliced `seq`
    :rtype: generator
    """
    # for pos in range(0, len(seq), size):
    #     yield seq[pos:pos + size]
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class ppdefaultdict(defaultdict):
    """
    Helper for cleaner ``pprint`` output.

    Source comes from `Stack Overflow <http://stackoverflow.com/a/12925062>`_
    """
    __repr__ = dict.__repr__


def infinite_dd():
    """
    When passed to a ``defaultdict``, this will allow for an infinitely-deep
    ``defaultdict``
    
    Source comes from `Stack Overflow <http://stackoverflow.com/a/4178334/1993468>`_
    """
    return ppdefaultdict(infinite_dd)
    
class keydefaultdict(ppdefaultdict):
    """
    Creates the default object at the index, but also passes the index as a
    parameter to the object's `__init__`
    
    Source comes from
    `Stack Overflow <http://stackoverflow.com/a/2912455/1993468>`_
    """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


def ensure_key(keymodule, valmodule):
    r"""
    If a given key does not exist in `self.items`, create it with an
    instance of the given value.

    This mimics the functionality provided by ``defaultdict``. This should
    only be used to override the ``defaultdict`` value for ``Host`` (which
    is a ``list``).

    :param keymodule: Class object to check for
    :param valmodule: Class to instantiate and assign if key does not exist
    """

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if keymodule not in args[0].host.items:
                if issubclass(valmodule.__class__, defaultdict):
                    args[0].host.items[keymodule] = valmodule
                else:
                    args[0].host.items[keymodule] = valmodule()
            return func(*args, **kwargs)
        return wrapper
    return decorate

class MetaExistsException(Exception):
    """When a Meta* instance runs into conflict!"""


class MetaList(list):
    r"""
    An ugly extension of ``list`` with the ability to search for values using
    metadata fields
    
    The class behaves (mostly) like a list: append, extend, insert, and pop
    at a will. However, if any object assigned to it has a `._meta` list, the
    ``MetaList`` instance will go through the attribute names and add their
    values to a hidden, internal dictionary. You can then search for these
    by passing a string into the index brackets.
    
    For example:
    
    .. code-block::python
    
        class MetaItem(ConfigItem):
            def __init__(self, name=None, number=None):
            # We will change empty strings to None
            if name:
                self._name = str(name)
            else:
                self._name = None
            if number is not None:
                self._number = int(number)
            else:
                self._number = None
            self._metalists = WeakList()
            super(MetaItem, self).__init__()

        _meta = ['name', 'number']

        def __repr__(self):
            return '<MetaItem name="{}" number="{}">'.format(self.name, self.number)

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, value):
            if value is None:
                for ml in self._metalists:
                    del ml[str(self._name)]
            else:
                value = str(value)
                for ml in self._metalists:
                    ml._update_meta(str(self.name), str(value), self)
                self._name = value
            
        @property
        def number(self):
            return self._number

        @number.setter
        def number(self, value):
            if value is None:
            for ml in self._metalists:
                del ml[str(self._number)]
            else:
                value = int(value)
                for ml in self._metalists:
                    ml._update_meta(str(self.number), str(value), self)
                self._number = value


        if __name__ == '__main__':
            mlist = MetaList([MetaItem(name, number) for name, number in
                                ('Alpha', 1), ('Beta', 2), ('Charlie', 3)])
            print metalist[0].name   # 'Alpha'
            print metalist[1].number # 2
            print metalist['Beta']   # <MetaItem name="Beta" number="2">
            c = metalist.pop()
            print metalist           # [<MetaItem name="Alpha" number="1">,
                                     #  <MetaItem name="Beta" number="2">]
            metalist.insert(0, c)
            print metalist           # [<MetaItem name="Charlie" number="3">,
                                     #  <MetaItem name="Alpha" number="1">,
                                     #  <MetaItem name="Beta" number="2">]
            del metalist[0]          # [<MetaItem name="Alpha" number="1">,
                                     #  <MetaItem name="Beta" number="2">]
            metalist['Alpha'].number = 4
            print metalist['4']      # <MetaItem name="Alpha" number="4">
            print metalist           # [<MetaItem name="Alpha" number="4">,
                                     #  <MetaItem name="Beta" number="2">]
            
            
    """
    def __init__(self, items=list(), overwrite=False):
        self._overwrite = overwrite
        self._meta = weakref.WeakValueDictionary()
        list.__init__(self, items)
        for item in items:
            if self._is_meta_friendly(item):
                self._add_meta(item)
    
    def _add_meta(self, item):
        added_self = False
        for meta in item._meta:
            m = getattr(item, meta)
            if m is None:
                continue
            if m in self._meta and not self._overwrite:
                raise MetaExistsException(
                    'Something already exists for {}!'.format(item))
            self._meta.update({str(m): item})
            added_self = True
        if added_self and self not in item._metalists:
            item._metalists.append(self)

    def _update_meta(self, oldkey, newkey, item):
        try:
            self._meta[str(newkey)] = item
            del self._meta[str(oldkey)]
        except KeyError:
            pass
        
    def _del_meta(self, item):
        for meta in item._meta:
            try:
                del self._meta[str(getattr(item, meta))]
            except KeyError:
                pass
        item._metalists.remove(self)
    
    @classmethod
    def _is_meta_friendly(cls, item):
        return (issubclass(item.__class__, ConfigItem) and
                hasattr(item, '_meta') and
                hasattr(item, '_metalists') and
                isinstance(item._metalists, WeakList))

    def _pre_check_adding_from_iter(self, items):
        metadata = dict()
        metalists_to_change = []
        # extend, __add__, and __iadd__ are all-or-nothing methods. We cannot
        # use ._add_meta() yet or else we will have invalid references!
        for item in items:
            if self._is_meta_friendly(item):
                add_to_metalist = False
                for meta in item._meta:
                    data = getattr(item, meta)
                    if data is not None:
                        if data in self._meta and not self._overwrite:
                            raise MetaExistsException(
                                'Already have metadata with {}!'.format(
                                    getattr(item, meta)))
                        metadata.update({str(data): item})
                        add_to_metalist = True
                if add_to_metalist:
                    metalists_to_change.append(item._metalists)
        return metadata, metalists_to_change
    
    def __getitem__(self, index):
        if not isinstance(index, int):
            return self._meta[index]
        else:
            return list.__getitem__(self, index)
        
    def __setitem__(self, index, item):
        olditem = list.__getitem(self, index)
        for meta in olditem()._meta:
            oldval = getattr(item, meta)
            if oldval is not None:
                if isinstance(oldval, int):
                    oldval = str(oldval)
                del self._meta[oldval]
        for meta in item._meta:
            newval = getattr(item, meta)
            if newval is not None:
                if isinstance(newval, int):
                    newval = str(newval)
                self._meta[newval] = item
        return list.__setitem__(self, index, item)
    
    def __delitem__(self, index):
        item = self.__getitem__(index)
        if self._is_meta_friendly(item):
            self._del_meta(item)
        if not isinstance(index, int):
            index = list.index(self, item)
        list.__delitem__(self, index)
        
    def __add__(self, other):
        raise NotImplementedError('Coming soon! (TM)')
        
    def __iadd__(self, other):
        metadata, metalists_to_change = self._pre_check_adding_from_iter(other)
        l = list.__iadd__(self, other)
        self._meta.update(metadata)
        for mlist in metalists_to_change:
            if self not in mlist:
                mlist.append(self)
        return l
        
    def append(self, item):
        list.append(self, item)
        if self._is_meta_friendly(item):
            self._add_meta(item)

    def insert(self, index, item):
        l = list.insert(self, index, item)
        if self._is_meta_friendly(item):
            self._add_meta(item)
        return l
    
    def extend(self, items):
        metadata, metalists_to_change = self._pre_check_adding_from_iter(items)
        l = list.extend(self, items)
        self._meta.update(metadata)
        for mlist in metalists_to_change:
            if self not in mlist:
                mlist.append(self)
        return l
    
    def pop(self, index=-1):
        item = list.pop(self, index)
        if self._is_meta_friendly(item):
            for m in item._meta:
                try:
                    del self._meta[str(getattr(item, m))]
                except KeyError:
                    pass
            item._metalists.remove(self)
        return item
