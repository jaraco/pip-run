import itertools
import functools


@functools.singledispatch
def items(input):
    r"""
    Convert an input to an iterable of items,
    comparable to pkg_resources.yield_lines

    >>> list(items('foo\nbar\n#baz'))
    ['foo', 'bar']

    >>> list(items(['foo', 'bar']))
    ['foo', 'bar']
    """
    return itertools.chain.from_iterable(map(items, input))


def is_comment(line):
    return line.startswith('#')


@items.register(str)
def _(text):
    """
    If the input is a string, split it, strip it, and remove comments.
    """
    stripped = (line.strip() for line in text.splitlines())
    clean = filter(None, stripped)
    return itertools.filterfalse(is_comment, clean)
