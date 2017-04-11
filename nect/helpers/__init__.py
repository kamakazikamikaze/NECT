from collections import defaultdict


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


class keydefaultdict(defaultdict):
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