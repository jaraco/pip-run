class Value(str):
    """
    >>> v = Value('foo; bar=baz; bing=bar')
    >>> v
    'foo'
    >>> v.bar
    'baz'
    >>> v.bing
    'bar'
    """

    def __new__(cls, val):
        key, _, rest = val.partition(';')
        self = super().__new__(cls, key)
        vars(self).update(cls.parse_attrs(rest))
        return self

    @staticmethod
    def parse_attrs(defn):
        for item in filter(None, defn.split(';')):
            yield map(str.strip, item.split('=', 1))
