import importlib
import os
import re


class Strategy(str):
    params: dict[str, str]

    @classmethod
    def resolve(cls, spec):
        """
        Resolve a strategy spec to a strategy name and context params.

        >>> Strategy.resolve('destroy')
        'destroy'
        >>> Strategy.resolve('persist').params
        {}
        >>> Strategy.resolve('persist; max-age=86400').params
        {'max_age': '86400'}
        >>> Strategy.resolve('persist; max age=86400; other=true').params
        {'max_age': '86400', 'other': 'true'}
        """
        name, sep, rest = spec.partition(';')
        strat = cls(name)
        strat.params = dict(filter(None, map(clean_param, rest.split(';'))))
        return strat


def make_var(name):
    return re.sub(r'[ -]+', '_', name.strip())


def clean_param(pair):
    name, sep, value = pair.partition('=')
    return name and (make_var(name), value and value.strip())


def strategy():
    spec = os.environ.get('PIP_RUN_RETENTION_STRATEGY') or 'destroy'
    strat = Strategy.resolve(spec)
    return importlib.import_module(f'.{strat}', package=__package__)
